# BOT. architecture

Sources of truth: `docs/DEVELOPMENT.md`, `CONTRIBUTING.md` and `pyproject.toml` in the repository. Where this file disagrees with them, the repository wins; run `/scan` for the current layout.

## Runtime

- Python 3.11 at minimum, 3.13 in deployment; CI tests 3.11, 3.12 and 3.13 on Ubuntu. No syntax newer than 3.11.
- discord.py 2.7. Dependencies are defined in `pyproject.toml`; `requirements*.txt` only install from it.
- Development often happens on Windows while CI runs on Linux: Windows-only code must still pass its tests on Linux.

## Startup and loading

- Entry point `python -m src.main` → `Bot` in `src/bot.py`.
- `setup_hook()` prepares shared helpers and the blacklist session, `load_cogs()` walks `src/cogs` with `pkgutil.walk_packages()` and loads each module, installs `CommandTranslator`, then syncs commands with `sync_global()` from `src/utils/command_sync.py`.
- Never call `tree.sync()` directly: with Discord Activities enabled it drops the activity's entry point command.
- One cog failing to load stops startup. Every non-package module under `src/cogs` needs `async def setup(bot)`; plain helpers belong in `src/utils`, business logic in `src/services`.
- Application commands are guild-only by default. Opening one to the personal app needs explicit `allowed_installs` and `allowed_contexts`, and code that copes with `interaction.guild` being `None`.

## Layers

| Path | Responsibility |
| --- | --- |
| `src/cogs/core` | Error handling, settings, logging, blacklist, appearance, language, dashboard API |
| `src/cogs/features` | Feature commands, interactive components, event listeners |
| `src/cogs/games` | Games |
| `src/services` | Business rules, settings changes, saving and public queries; also the LAN node code |
| `src/locales` | English and Chinese messages, command description translations, `/help` content |
| `src/utils` | Storage, background work, translation, language resolution, shared helpers |
| `src/control_panel` | Windows terminal control panel |
| `services/` | Standalone external integrations (GitHub); not cog services |
| `tests/` | Automated tests |

- Cogs handle Discord parameters, permissions, `defer`, embeds and messages; creating, changing and saving data happens in services.
- Public queries return independent copies. Never edit a service's `.config` or caches directly, or call `_load()` / `_save()`.
- A settings change keeps the guild's other features, other guilds' data, counters and unknown fields.
- A failed save raises: memory is not updated, success is not reported, nothing is overwritten with empty data. New state is published only after a successful save.

## Storage

- `STORAGE_BACKEND` is `json` or `mysql` (production uses MySQL 8.4 through PyMySQL).
- Documents go through `read_document()` / `write_document()` in `src/utils/document_store.py`. In MySQL mode the path is the key of a row in `documents`, holding the whole JSON and a SHA-256 checksum.
- Operational history, caches, metrics, audits, the message log and file-tool quotas have their own tables; both backends run the same SQL through `src/utils/mysql_compat.py`.
- A database failure never falls back to pre-migration JSON, and MySQL mode never reads or writes the old JSON files.
- Synchronous storage work always runs as `await run_storage(fn, ...)` (`src/utils/storage_worker.py`), with read, change and save in one job. Do not split them into several jobs, and do not overwrite with a stale copy after awaiting an external API.
- Keep existing encryption keys and cookie ciphertexts; never generate a new key over existing accounts when the original is missing.

## Bilingual interface

- Every member-facing text exists in English and Chinese: `MESSAGES` in `src/locales/<module>_messages.py`, used through `tx("key", v0=...)`.
- Entry points carry `@localized("interaction")` (or `"ctx"`, `"message"`, `"guild"`); views subclass `LocalizedView`.
- Command names are always English. Command and option descriptions are written in English in code, with the Chinese in `TEXT` of `src/locales/commands.py`; context menu names go in `CONTEXT_MENU_NAMES`.
- A new message module is added to the import and registration list in `src/locales/__init__.py`; duplicate keys fail at load time.
- `/help` content lives in `CATEGORIES` of `src/locales/help.py`; the English and Chinese section keys must match.
- Stored identifiers are never translated, only their display. Dashboard API responses, command-line tools and logs are not translated.

## Code style

- Clear English names. Comments and docstrings are English only and explain why; no conversation with tools or edit history.
- One section banner form only: `# ── Title ───`, padded with dashes to 68 characters.
- Logs describe the event, the state and the reason.

## Background work and interactions

- Background tasks are cancelled in `cog_unload()`; tasks that need Discord ready wait in `before_loop` on `wait_until_ready()`.
- Interactions are answered or deferred before slow work, and handle expiry (10062) and API timeouts.
- External network calls use async clients or background execution with timeouts, HTTPS and certificate verification.

## LAN nodes

- NovaGrid (`novagrid.py`, `tool_*.py`) and AI image review (`moderation_*.py`) are copied flat into packages: they support both import styles with `if __package__:` and never import other `src.` modules.
- Host and node compare source hashes (`engine_digest()`); changing the engine or review rules means rebuilding the package.
- Any failed step of the review node reports "undecided", never a pass.
