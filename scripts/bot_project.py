"""Local BOT. detection and opt-in acceptance checks; Python 3.11+."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit

FINGERPRINT = (
    "src/bot.py",
    "src/cogs",
    "src/locales/help.py",
    "src/utils/command_sync.py",
    "pyproject.toml",
)
ROOT_COMMIT = "94daa94685e308daf3d6c8a9a81a83b97a7d816a"
CHECKS = (
    ("pytest", ("pytest", "-v", "--cov=src", "--cov-report=xml")),
    ("flake8", ("flake8", "src", "services", "tests")),
    ("black", ("black", "--check", "src", "services", "tests")),
    ("isort", ("isort", "--check-only", "src", "services", "tests")),
    ("bandit", ("bandit", "-r", "src", "services", "-ll")),
)


def git(cwd, *args):
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        return (
            result.stdout
            if result.returncode == 0 and "-z" in args
            else (result.stdout.strip() if result.returncode == 0 else None)
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def upstream(url):
    """Accept exact GitHub repositories, never lookalike hostname suffixes."""
    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:") :]
    else:
        parsed = urlsplit(url)
        if parsed.hostname != "github.com" or parsed.scheme not in {"https", "ssh"}:
            return False
        path = parsed.path.lstrip("/")
    return path.rstrip("/").removesuffix(".git").lower() == "keeiv/bot"


def scan(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel")
    if not top:
        return {"active": False, "reason": "Not inside an accessible Git checkout"}
    root = Path(top)
    missing = [name for name in FINGERPRINT if not (root / name).exists()]
    if missing:
        return {
            "active": False,
            "reason": "Missing BOT. fingerprint paths",
            "missing": missing,
        }
    try:
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
            "project"
        ]
    except (OSError, ValueError, KeyError):
        return {"active": False, "reason": "Invalid project metadata"}
    if project.get("name") != "discord-bot":
        return {"active": False, "reason": "Project name is not discord-bot"}
    remotes = []
    for name in (git(root, "remote") or "").splitlines():
        if upstream(git(root, "remote", "get-url", name) or ""):
            remotes.append(name)
    shared = (
        ROOT_COMMIT
        in (git(root, "rev-list", "--max-parents=0", "HEAD") or "").splitlines()
    )
    related = bool(remotes or shared)
    hint = git(root, "config", "--get", "bot-dev.role") or ""
    # Same rule as the Claude plugin: origin is keeiv/bot and the local Git user is
    # keeiv. Both are editable, so this is only a workflow hint, never authorization.
    user = (git(root, "config", "--get", "user.name") or "").strip().lower()
    maintains = "origin" in remotes and user == "keeiv"
    if hint in {"owner", "contributor"}:
        role = hint
    elif maintains:
        role = "owner"
    else:
        role = "contributor" if related else "derivative"
    status = git(root, "status", "--porcelain=v1", "-z") or ""
    # Parse NUL records so filenames containing spaces/newlines stay distinct.
    records = status.split("\0")
    changes = []
    i = 0
    while i < len(records):
        row = records[i]
        if row:
            changes.append({"status": row[:2], "path": row[3:]})
            if "R" in row[:2] or "C" in row[:2]:
                i += 1
        i += 1

    def modules(folder):
        return sorted(
            p.stem for p in (root / folder).glob("*.py") if p.name != "__init__.py"
        )

    return {
        "active": True,
        "root": str(root),
        "version": project.get("version"),
        "relationship": "upstream-or-fork" if related else "derivative",
        "upstream_remotes": remotes,
        "shares_known_root": shared,
        "role_hint": role,
        "role_is_authorization": False,
        "branch": git(root, "branch", "--show-current") or "(detached)",
        "head": git(root, "rev-parse", "HEAD"),
        "changes": changes,
        "modules": {
            folder: modules(folder)
            for folder in (
                "src/cogs/core",
                "src/cogs/features",
                "src/cogs/games",
                "src/services",
                "src/locales",
            )
        },
        "test_files": len(list((root / "tests").rglob("test_*.py"))),
    }


def check(cwd, python=None, timeout=600):
    state = scan(cwd)
    if not state["active"]:
        print(json.dumps(state, ensure_ascii=False))
        return 2
    root = Path(state["root"])
    interpreter = (
        Path(python)
        if python
        else root
        / ".venv"
        / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if not interpreter.is_file():
        print(
            "No virtual environment interpreter; pass --python explicitly.",
            file=sys.stderr,
        )
        return 2
    env = {k: v for k, v in os.environ.items() if not k.startswith("MYSQL_")}
    env.update(
        {
            "PYTHON_DOTENV_DISABLED": "1",
            "STORAGE_BACKEND": "json",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    results = []
    for name, args in CHECKS:
        print(f"Running {name}", flush=True)
        try:
            run = subprocess.run(
                [str(interpreter.resolve()), "-m", *args],
                cwd=root,
                env=env,
                timeout=timeout,
            )
            results.append({"check": name, "exit_code": run.returncode})
        except subprocess.TimeoutExpired:
            results.append({"check": name, "exit_code": 124, "timeout": True})
        except OSError as error:
            results.append(
                {"check": name, "exit_code": 127, "error": type(error).__name__}
            )
    print(json.dumps({"results": results, "mysql_integration": "not run"}, indent=2))
    return int(any(row["exit_code"] != 0 for row in results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("scan", "check"))
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--python")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.mode == "scan":
        print(json.dumps(scan(args.cwd), indent=2, ensure_ascii=False))
        return 0
    return check(args.cwd, args.python, args.timeout)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
