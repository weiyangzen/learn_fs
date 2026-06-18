# sources/sync-backup/rsync/testsuite/stop-time_test.py

Purpose: covers `--stop-at` absolute-time parsing and `--stop-after` minute-count parsing, especially option paths that may be otherwise untested.

Important APIs and flow: builds a depth-2 data tree with `make_tree()`, records relative file paths, and computes a future timestamp one day from the current time in `%Y-%m-%dT%H:%M` format. It runs `rsync -a --stop-at=<future>` and asserts every file matches. It then runs a known-past `--stop-at=2000-01-01T00:00` with `check=False` and fails if parsing allows a successful transfer. Finally it runs `--stop-after=60` and asserts content equality.

State and persistence: destination is removed before each scenario. Time dependence is deliberate but uses a one-day future value to avoid fixed-date rot and 32-bit `time_t` overflow.

Dependencies and integration: exercises option parsing in rsync’s time handling and normal transfer continuation when limits are not reached. Risks include clock skew only inside the current process; test signal is parse rejection for past time and successful content copies for future/minute cases.
