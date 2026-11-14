---
name: bot-scan
description: Scan a BOT. checkout to report repository identity, branch, dirty paths, role hints and module counts without reading secrets or changing files.
---

Run `python "<plugin-root>/scripts/bot_project.py" scan --cwd "<working-directory>"`, resolving plugin-root as `../..` relative to this skill. Report inactive status when outside BOT. A role hint is not permission. Explain the observed version, Git state and module counts in the user's language. Do not fetch, run tests, start the bot or read credentials for a scan.
