# BOT. acceptance and done criteria

Sources of truth: `CONTRIBUTING.md`, `docs/DEVELOPMENT.md` and `.github/workflows/ci.yml` in the repository.

## When a change is done

All of these must hold before calling it done. Anything not done is reported as "not run" or "not finished", never as delivered.

1. **Correct behaviour**: the requirement is met, and the related code and its callers were read; the fix is not cosmetic.
2. **Tests**: when adding or changing saving logic, cover at least the normal path, a failed save, copy isolation and preservation of existing fields; for external lookups, also the case where settings change while waiting. Tests check observable behaviour, do not copy implementation details, and never touch production services, real tokens, cookies or user data.
3. **The same checks as CI all pass** (from the repository root):

   ```bash
   python -m isort src services tests
   python -m black src services tests
   python -m pytest -q
   python -m flake8 src services tests
   python -m black --check src services tests
   python -m isort --check-only src services tests
   python -m bandit -r src services -ll
   ```

   CI also runs the integration tests on MySQL 8.4: `tests/test_mysql_storage.py`, `test_storage_reliability.py`, `test_service_boundaries.py`, `test_achievement_storage.py`, `test_content_alignment.py`, `test_tool_mysql.py`. Without a dedicated `_test` database they skip locally, which is expected; a successful isolated integration run locally or in CI is needed to verify MySQL code paths.

4. **Both languages**: new member-facing text exists in English and Chinese with the same placeholders; new command descriptions have a Chinese translation. `tests/test_i18n.py` checks this.
5. **Comment style**: `tests/test_comment_style.py` checks tracked files only, so `git add` new files before running it.
6. **Docs in step**: a change to public behaviour, commands, settings or data formats is reflected in both READMEs, `docs/` and `/help`.
7. **No secrets**: the diff contains no tokens, passwords, keys, cookies, user data or database files.

## Text-only or documentation changes

Check the content, links and diff; no bot restart is needed. Formatting and tests still apply (for example, `/help` content is checked by `test_i18n.py`).

## Changes that need an issue first

New dependencies, data format or table changes, cross-module restructuring, and changes to existing commands or permissions: describe the goal, compatibility and migration first, then implement.

## Storage changes

Verify compatibility with existing data. Before a migration stop every writer, back up the original JSON / SQLite files and the encryption keys, and compare source hashes, document contents and table rows. A failed migration rolls back; original files and backups are never deleted.

## Security checklist (every change)

- Every submitted line was read and understood.
- No hard-coded tokens, passwords or keys; secrets never reach logs, error messages or replies.
- User input never reaches a shell, SQL, a file path or a URL unchecked.
- No existing permission check, origin check or rate limit is loosened or bypassed.
- External requests use HTTPS, keep certificate verification and set timeouts.
- New dependencies are real, maintained and free of known high-risk advisories.
- Changes touching permissions, credentials, uploads or external connections come with tests and pass Bandit.
