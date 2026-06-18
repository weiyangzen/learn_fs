# sources/test-tools/kdevops/playbooks/python/workflows/fstests/lib/git.py

Purpose: Minimal git helper module used by fstests expunge tooling to determine whether a file is untracked.

Key APIs and flow: Defines `GitError`, `ExecutionError`, and `TimeoutExpired` exception classes plus `_check()` for return-code enforcement. `is_new_file(file)` runs `git status -s <file>` with a one-second timeout and returns `True` if output starts with `??`, `False` for nonzero git exit or tracked files, and the string `"Timeout"` if `communicate()` times out.

State, dependencies, integration: Uses `subprocess.Popen`; it does not mutate repository state. Integrated by `get_new_expunge_files.py`.

Risks and test signals: Timeout returns a truthy string instead of raising or returning `False`; custom `TimeoutExpired.__init__()` returns a value ineffectively; `_check()` and imported `os` are unused; process cleanup is incomplete on timeout. Tests should mock git output for untracked/tracked/error/timeout and assert callers do not misinterpret timeout.
