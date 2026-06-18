## sources/sync-backup/bup/pylint

Purpose: repository wrapper for running pylint under Bup’s configured Python environment.

Important control flow: reads `config/config.var/with-pylint`. `yes` runs, `no` exits successfully with a message, and `maybe` runs only if `dev/have-pylint` succeeds. It prepends `test/lib` to `PYTHONPATH`. With no arguments it runs pylint on `lib`, then on tests with wildcard import warnings disabled; with arguments it execs pylint directly under `dev/bup-python`.

State and dependencies: depends on configure output, `dev/have-pylint`, `dev/bup-python`, and test support libraries. It changes only process environment.

Risks and tests: unexpected config values exit 2. The wrapper and `pytest` need synchronized environment behavior per comments. It is a developer quality gate rather than product runtime; no direct test in this subset.
