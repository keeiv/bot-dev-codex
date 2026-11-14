# BOT. tests

About 3000 tests under `tests/`, run with `python -m pytest -q` in under a minute.

## What every test gets (tests/conftest.py)

- The working directory is a fresh `tmp_path`, so `data/` paths land in a throwaway folder.
- `STORAGE_BACKEND=json`, `.env` loading disabled, a fixed test encryption key, and Discord, blacklist, GitHub and dashboard credentials removed from the environment.
- Sockets may connect only to `localhost`, `127.0.0.1` or `::1`; any other connection raises "Tests cannot connect to external services". Mock external APIs.
- `pytest-asyncio` runs in `auto` mode: `async def test_...` needs no marker.

## Tests that guard conventions

| Test | Fails when |
| --- | --- |
| `tests/test_i18n.py` | a message lacks `en` or `zh`, placeholders differ, `/help` sections differ between languages, a command description is not English or has no Chinese, a translation exceeds Discord limits, a context menu lacks a Chinese name, a literal key passed to `tx()` / `t()` does not exist, or a dynamic key (achievements, settings categories) is missing |
| `tests/test_comment_style.py` | a tracked file has a non-English comment or docstring, or a section banner in another form; it reads tracked files only, so `git add` new files first |
| `tests/test_bot_startup.py` | the bot cannot be built or a cog under `src/cogs` fails to load |
| `tests/test_data_browser.py` | the control panel's labels or browser behaviour change |
| `tests/test_control_panel.py` | the control panel's hotkeys change |

## MySQL

`tests/test_mysql_storage.py`, `test_storage_reliability.py`, `test_service_boundaries.py`, `test_achievement_storage.py`, `test_content_alignment.py` and `test_tool_mysql.py` hold tests that need `MYSQL_INTEGRATION_TEST=1` and a database whose name ends in `_test`. Locally they skip; CI runs them against MySQL 8.4. Never point them at a production database.

## Writing a test

- Check what a member or the data would see: the reply, the saved document, the refusal. Do not copy the implementation.
- For saving logic cover the normal path, a failed save (memory unchanged, error raised), copy isolation and preservation of unknown fields.
- Build Discord objects with `SimpleNamespace`, `Mock` and `AsyncMock`, as the existing tests do; no real token or guild.
- Windows-only code must pass on Linux too: inject or replace `msvcrt`, `ctypes.windll` and PowerShell calls.
