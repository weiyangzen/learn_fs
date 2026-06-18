# File Research: sources/local-fs/dlm/python/tests/recovery_interrupt

## Purpose
Python test/stress script that repeatedly creates and destroys a DLM lockspace, optionally doing lock activity, until interrupted.

## Behavior
- Imports `Lockspace` from `dlm`.
- Handles SIGINT by setting a global `end` flag.
- Options:
  - `--lock` / `-l` to lock/unlock resource `fooobaar` each cycle.
  - `--wait` / `-w` to sleep while holding the lock.
  - `--debug` / `-d` for logging level.
- Loop creates a default lockspace, optionally creates and locks a resource, sleeps, unlocks, deletes lock, deletes lockspace, and logs each step.

## Dependencies
- Relies on local/importable `dlm.py` wrapper and working `libdlm_lt`/kernel DLM environment.

## Risks / Gaps
- Uses destructor side effects for cleanup via `del`, which depends on CPython reference counting behavior.
- No exception handling inside the loop, so a DLM operation failure aborts the test.
