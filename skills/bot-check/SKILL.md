---
name: bot-check
description: "Run BOT. acceptance checks using its virtual environment: pytest, flake8, black, isort and bandit, with explicit failures and timeouts."
---

For an explicit request to run checks, inspect `.github/workflows/ci.yml` for drift first, then run `python "<plugin-root>/scripts/bot_project.py" check --cwd "<working-directory>"`. Resolve plugin-root as `../..` relative to this file. This executes repository code, writes pytest coverage output and may take minutes; it does not format source, start the bot, commit or push. Without a checkout virtual environment, require `--python <interpreter>` rather than silently choosing a global installation.

Report every exit code, timeout and skipped test. If CI differs from the bundled command list, use current CI commands and disclose the difference. An isolated MySQL integration run requires a separately configured test database; never point tests at production or claim skipped MySQL paths were verified. The runner removes inherited MYSQL integration/connection variables so ordinary checks do not unexpectedly connect to a real database.

If the Nova true-color test fails because ANSI RGB sequences are absent, check whether `NO_COLOR` is inherited. Re-run only that failing test with `NO_COLOR` temporarily removed in the child environment, restore the original environment and report both runs. Do not silently hide the failure or claim the original full suite passed.
