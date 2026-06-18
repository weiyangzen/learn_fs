## sources/sync-backup/bup/pytest

Purpose: repository wrapper for running pytest with Bup’s Python and default test selection.

Important control flow: shell prelude sets `BUP_DIR` and `GIT_DIR` to `/dev/null`, prepends `test/lib` to `PYTHONPATH`, and execs `dev/bup-python` on the script itself. Python code defaults to `pytest -v -m 'not release'`. If `xdist` is installed it enables work stealing for versions at least 3.2.1 and preserves user args; otherwise it strips `-n` options before invoking pytest.

State and dependencies: no persistent state; depends on `pytest`, optional `xdist`, `shlex`, `sys`, and the repo’s `conftest.py`.

Risks and tests: argument filtering only handles common `-n` forms. Mark defaults mean release tests are excluded unless requested. It is exercised whenever the suite is run, and `pytest.ini` supplies collection roots and marker declaration.
