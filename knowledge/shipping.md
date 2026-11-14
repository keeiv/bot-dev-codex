# BOT. commits, pushes and pull requests

Sources of truth: `CONTRIBUTING.md` and `docs/DEVELOPMENT.md` in the repository.

## Commit messages

- First line `type: summary in Traditional Chinese`, with type `feat`, `fix`, `docs`, `style`, `refactor`, `test` or `chore`.
- When more is needed, a blank line and a Chinese body saying what changed and why (often a `- ` list).
- Read `git log -3 --format=%B` first and follow the existing style.

## Commit only what belongs to the change

- Stage explicit paths; never `git add -A`.
- Never commit: `.env`, `data/` (node packages and runtime data included), node pairing files and keys (`.file-tools-worker.json`, `.image-review-worker.json`, `worker.json`, `worker-key.pem`), `run_bot*.bat`, `bot-panel.ico`, tokens, passwords, encryption keys, cookies, user data, database files or local backups.
- Look at `git status` before committing and scan the staged diff for anything that looks like a token or key.

## By role

### Owner (maintainer)

- Within the agreed scope, commit straight to `main` and push; no pull request.
- Before committing: fetch and verify the baseline against origin. After creating local commits, being ahead is expected; verify there are no unseen remote commits before pushing. Run the relevant checks in done.md.
- After pushing: confirm `0 0` again and wait for the GitHub Actions `CI Pipeline` to finish (it includes the MySQL integration job).
- Force pushes and history rewrites need explicit consent every time.

### Contributor

- Use a fork and a pull request; never push to keeiv/bot directly.
- The PR title uses the same Conventional Commits prefix plus a Traditional Chinese summary.
- The PR body states the problem, the behaviour after the change and the verification; for data migrations add backup, compatibility and rollback; link any related issue.
- A PR with a security risk is not merged (see the security checklist in done.md).
- The bot and the website are separate repositories; cross-project changes are submitted separately.

## License

AGPL-3.0-only, author Keeiv. New contributions use the same license and keep contributors' and third-party copyright notices.
