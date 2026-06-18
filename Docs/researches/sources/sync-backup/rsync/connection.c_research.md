# sources/sync-backup/rsync/connection.c

## Purpose
Implements daemon max-connection accounting by locking fixed byte ranges in a module lock file.

## Important APIs, Types, and Functions
`claim_connection(char *fname, int max_connections)` returns 1 when a slot is claimed and 0 when the lock file cannot be opened or all slots are locked. It uses `open(O_RDWR|O_CREAT, 0600)` and `lock_range(fd, i*4, 4)` for each possible slot.

## Control Flow
If `max_connections` is 0, the function immediately permits the connection. Otherwise it opens/creates the lock file, scans slot ranges from 0 to `max_connections - 1`, and returns success while intentionally keeping the descriptor open for the process lifetime. If no range can be locked it closes the descriptor, sets `errno = 0`, and returns failure.

## State and Persistence Behavior
Creates or reuses the configured lock file and relies on advisory byte-range locks held by open file descriptors. Lock state is process/kernel state, released when the daemon worker exits or closes the descriptor.

## Dependencies and Integration Points
Used by `clientserver.c` in `rsync_module()` for the daemon `max connections` setting. Depends on `lock_range()` portability wrappers and daemon parameter values from `lp_lock_file()` / `lp_max_connections()`.

## Risks and Test Signals
Risks include filesystems without reliable advisory locking, descriptor leakage expectations, stale lock files that are harmless but confusing, and ambiguous failure handling where open failures are distinguished from capacity by `errno`. Test signals include parallel daemon connections at and above the configured limit, invalid/unwritable lock-file paths, and process exit releasing a slot.
