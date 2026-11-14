import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "bot_project", Path(__file__).parents[1] / "scripts/bot_project.py"
)
bot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bot)


class DetectionTests(unittest.TestCase):
    def test_exact_remote(self):
        for url in (
            "https://github.com/keeiv/bot.git",
            "git@github.com:keeiv/bot.git",
            "ssh://git@github.com/keeiv/bot",
        ):
            self.assertTrue(bot.upstream(url))
        for url in (
            "https://evilgithub.com/keeiv/bot",
            "https://github.com/keeiv/bot-extra",
            "https://github.com/keeiv/bot/other",
        ):
            self.assertFalse(bot.upstream(url))

    def test_outside_git(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(bot.scan(folder)["active"])

    def test_checkout_and_subdirectory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", folder], check=True)
            for name in bot.FINGERPRINT:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                if name == "src/cogs":
                    p.mkdir(exist_ok=True)
                else:
                    p.write_text(
                        (
                            '[project]\nname="discord-bot"\nversion="1.2.3"\n'
                            if name == "pyproject.toml"
                            else ""
                        ),
                        encoding="utf-8",
                    )
            subprocess.run(
                [
                    "git",
                    "-C",
                    folder,
                    "remote",
                    "add",
                    "upstream",
                    "https://github.com/keeiv/bot.git",
                ],
                check=True,
            )
            state = bot.scan(root / "src")
            self.assertTrue(state["active"])
            self.assertEqual(state["role_hint"], "contributor")
            self.assertFalse(state["role_is_authorization"])
            self.assertEqual(state["version"], "1.2.3")
            (root / "pyproject.toml").write_text(
                '[project]\nname="other"', encoding="utf-8"
            )
            self.assertFalse(bot.scan(root)["active"])

    def test_owner_needs_origin_and_git_user(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", folder], check=True)
            for name in bot.FINGERPRINT:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                if name == "src/cogs":
                    p.mkdir(exist_ok=True)
                else:
                    p.write_text(
                        '[project]\nname="discord-bot"\nversion="1.2.3"\n'
                        if name == "pyproject.toml"
                        else "",
                        encoding="utf-8",
                    )
            git = ["git", "-C", folder]
            subprocess.run([*git, "remote", "add", "origin", "https://github.com/keeiv/bot.git"], check=True)
            subprocess.run([*git, "config", "user.name", "Someone"], check=True)
            self.assertEqual(bot.scan(root)["role_hint"], "contributor")
            subprocess.run([*git, "config", "user.name", "keeiv"], check=True)
            self.assertEqual(bot.scan(root)["role_hint"], "owner")
            subprocess.run([*git, "remote", "set-url", "origin", "https://github.com/someone/bot.git"], check=True)
            # Not keeiv/bot and no shared history: neither a maintainer nor a fork of it.
            self.assertEqual(bot.scan(root)["role_hint"], "derivative")

    def test_checks_failure_timeout_and_mysql_isolation(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / "python"
            executable.touch()
            observed = []

            def run(argv, **kwargs):
                observed.append(kwargs["env"])
                if "black" in argv:
                    raise subprocess.TimeoutExpired(argv, 1)
                return subprocess.CompletedProcess(argv, 1 if "flake8" in argv else 0)

            with patch.object(
                bot, "scan", return_value={"active": True, "root": folder}
            ), patch.object(bot.subprocess, "run", side_effect=run), patch.dict(
                bot.os.environ,
                {"MYSQL_INTEGRATION_TEST": "1", "MYSQL_PASSWORD": "fake-test-value"},
            ):
                self.assertEqual(bot.check(folder, executable, 1), 1)
            self.assertEqual(len(observed), 5)
            self.assertTrue(
                all(not any(k.startswith("MYSQL_") for k in env) for env in observed)
            )


if __name__ == "__main__":
    unittest.main()
