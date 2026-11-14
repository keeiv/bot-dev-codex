# BOT. recipes

Step-by-step for the changes that come up most. Each ends with the checks in done.md. Paths are from the repository root.

## Add a slash command to an existing feature

1. In the feature's cog (`src/cogs/<core|features|games>/<feature>.py`), add the command with an English `description` and English `@app_commands.describe(...)` texts.
2. Put `@localized("interaction")` under the command decorator so `tx()` speaks the right language.
3. Validate parameters and Discord permissions in the cog; call the feature's service for any change to data, through `await run_storage(service.method, ...)`.
4. `defer` before anything slow, then answer with `followup`. Handle an expired interaction (Discord error 10062).
5. Add every reply text to `src/locales/<feature>_messages.py` with `"en"` and `"zh"` and identical placeholders.
6. Add the Chinese for the description and every option description to `TEXT` in `src/locales/commands.py`.
7. If members should find it, add a line to the matching section of `CATEGORIES` in `src/locales/help.py`, in both languages.
8. Guild-only is the default. For the personal app, add `@app_commands.allowed_installs(guilds=True, users=True)` and `@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)` and handle `interaction.guild is None`.
9. Test the observable behaviour (reply, saved data, refusal without permission) in `tests/`.

## Add a new feature module

1. Service in `src/services/<feature>_service.py`: owns loading, changing and saving; public queries return copies; a failed save raises and leaves memory untouched.
2. Cog in `src/cogs/features/<feature>.py` (or `core` / `games`) ending with `async def setup(bot): await bot.add_cog(...)`. It is loaded automatically; a load error stops the bot, so import errors surface at startup.
3. A new `src/locales/<feature>_messages.py` exporting `MESSAGES`, registered in the import and registration list of `src/locales/__init__.py`. Duplicate keys fail at load.
4. Background loops start in `cog_load` or with `tasks.loop`, wait for `wait_until_ready()` in `before_loop`, and are cancelled in `cog_unload()`. A loop survives one failed iteration: catch, log and continue.

## Store a new document or field

1. Read and write it through `read_document()` / `write_document()` in `src/utils/document_store.py`, using a path such as `data/storage/<feature>.json` as the key; never open the file directly.
2. Keep unknown fields, other guilds' data and counters when you write.
3. Add the Chinese name of the document to `DOCUMENTS` and of each new field to `WORDS` in `src/control_panel/labels.py`, so the control panel's database browser can show it (`tests/test_data_browser.py` covers the lookups).
4. A field holding IDs as keys (servers, members, channels) gets its kind in `ID_KINDS`, so `1461…` reads as a server or a member.
5. Name a secret field so it matches `SENSITIVE` in the same file (it contains `token`, `cookie`, `secret`, `password`, `api_key` and the like): the browser then masks it and never lets it be edited.

## Add a table

1. Write SQL that both backends accept: SQLite through `src/utils/database_manager.py` style code and MySQL through `src/utils/mysql_compat.MySQLConnection` (it rewrites `?` to `%s` and `INSERT OR REPLACE` to `REPLACE`).
2. If existing JSON or SQLite data has to move, extend `src/migrate_storage.py` so the migration copies and verifies it.
3. Add the MySQL behaviour to a test in the integration set (`tests/test_mysql_storage.py` and its neighbours listed in done.md); it runs in CI.

## Change text only

1. Edit the `MESSAGES` entry or `TEXT` translation; keep placeholders identical in both languages.
2. Run `python -m pytest tests/test_i18n.py -q`; no restart of the bot is needed to verify.

## Sync commands

Use `sync_global(bot.tree)` from `src/utils/command_sync.py`. Plain `tree.sync()` removes the Discord Activity entry point command.
