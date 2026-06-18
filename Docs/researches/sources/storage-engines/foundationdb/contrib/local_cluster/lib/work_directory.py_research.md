# sources/storage-engines/foundationdb/contrib/local_cluster/lib/work_directory.py

## Purpose
`work_directory.py` manages filesystem directories used by local FoundationDB clusters for data and logs.

## Important APIs, Types, And Functions
`WorkDirectory(base_directory=None, data_directory="data/", log_directory="log/", auto_cleanup=False)` stores configuration. Properties expose `base_directory`, `data_directory`, and `log_directory`. `setup()` creates a temp base directory if needed, creates data and log subdirectories, and changes the process current working directory to the base. `teardown()` removes the base directory. Context manager methods call setup and optionally teardown.

## Control Flow
Entering the context or calling setup materializes directories and changes cwd. Exiting restores the original cwd and removes the directory only when `auto_cleanup` is true.

## State And Persistence Behavior
The class persists directories on local disk. With default `auto_cleanup=False`, temp work directories remain after use. It stores the original cwd at construction time for restoration.

## Dependencies And Integration Points
It depends on `tempfile`, `os`, `shutil`, and logging. `lib.local_cluster.FDBServerLocalCluster` creates a `WorkDirectory` directly and calls `setup` without using its context manager.

## Risks And Edge Cases
Changing process-wide cwd is surprising and not thread-safe. `teardown` deletes the full base directory recursively. If `setup` is called without the context manager, cwd is not automatically restored. Relative `data_directory` and `log_directory` values are joined to the base without normalization.

## Test Signals
Tests should verify temp and explicit base-directory setup, data/log creation, cwd restoration in context manager use, auto-cleanup behavior, and safe handling of repeated setup/teardown calls.
