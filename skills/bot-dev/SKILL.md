---
name: bot-dev
description: Develop, review or explain the BOT. Discord bot (keeiv/bot), including its cogs, services, storage, localization, acceptance and contribution workflow. Verify the checkout first; stay inactive in unrelated projects.
---

# BOT.dev for Codex

Run `python "<plugin-root>/scripts/bot_project.py" scan --cwd "<working-directory>"` first. Resolve plugin-root relative to this file (`../..`); never assume the user's checkout path. Use Python 3.11 or later. An inactive result means stop applying BOT.-specific rules. The skill remains discoverable outside BOT.; runtime detection gates its behavior, not its visibility.

Read the checkout's `AGENTS.md`, `CONTRIBUTING.md`, `docs/DEVELOPMENT.md` and `.github/workflows/ci.yml` as relevant. Repository instructions and current code take precedence over bundled snapshots. Existing user language preferences apply; otherwise the bundled output defaults to English. Do not inject a persona or change global language settings.

Read only the references needed, relative to plugin-root:
- `knowledge/architecture.md`: startup, cog/service split, storage and localization.
- `knowledge/map.md`: locating feature implementations.
- `knowledge/recipes.md`: adding commands, fields and tables.
- `knowledge/testing.md`: fixtures, isolation and relevant regression coverage.
- `knowledge/done.md`: acceptance and reporting evidence.
- `knowledge/shipping.md`: commits, PRs and release conventions, subject to the rules below.

Preserve `run_storage` transaction boundaries, save-before-publish behavior, bilingual messages and `sync_global` activity entry points. Tests must not touch production credentials or services. Do not read `.env` or runtime data merely to scan a project.

Role detection is a workflow hint, never authentication. Git names and `git config bot-dev.role` are editable. An explicit user statement that they maintain BOT. establishes the maintainer workflow for this task; do not infer push permission from a name. Within an authorized delivery scope, maintainers may push directly without a PR. Contributors use a fork and PR. Read-only reviews never edit, commit or push. Do not auto-run checks or publish merely because the skill loaded.

Before shipping inspect staged paths, preserve unrelated changes, run appropriate current checks and confirm the CI run matches the pushed SHA. Before committing compare with origin; after committing expect local commits ahead until pushed (do not require `0 0` before pushing a new commit). Never present old test totals as fresh evidence.

Use `$bot-scan` for an explicit status scan and `$bot-check` for CI-style checks. These are Codex skills, not Claude `/scan` commands or system-prompt hooks.
