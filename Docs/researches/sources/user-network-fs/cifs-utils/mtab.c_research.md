<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mtab.c -->
# sources/user-network-fs/cifs-utils/mtab.c

## Purpose

`mtab.c` implements legacy `/etc/mtab` usability checks, locking, unlocking, and safe close/fsync helpers for `mount.cifs`.

## Important APIs, Types, and Functions

Important functions are `mtab_unusable`, `unlock_mtab`, `lock_mtab`, and `my_endmntent`; internal helpers include signal handlers and `mono_time`.

## Control Flow

`mtab_unusable` rejects missing or symlinked mtab. `lock_mtab` installs signal handlers, creates a per-pid link target, attempts to atomically link it to the mtab lock path, and combines link ownership with `fcntl` locking and a 30-second timeout. `unlock_mtab` removes the lock file only if this process created it. `my_endmntent` flushes and fsyncs the mtab stream, truncating back to a known size on failure before closing.

## State and Persistence Behavior

Static state tracks whether this process created the lock, the lock fd, and whether signal handlers were installed. Persistent filesystem state includes `_PATH_MOUNTED_LOCK` and temporary link-target files.

## Dependencies and Integration Points

It depends on system mtab paths, fcntl locks, signals, monotonic time when available, and `mount.h`. `mount.cifs.c` calls it before adding or deleting mtab entries.

## Risks and Edge Cases

Signal handler installation is broad and can alter process signal behavior after mtab work. Stale lock files, read-only filesystems, symlinked mtab, and concurrent mount processes are the main edge cases. Timeout arithmetic uses seconds only for the stop condition.

## Test Signals

Tests should simulate concurrent lockers, stale locks, symlinked `/etc/mtab`, fsync failure/truncation, signal interruption, and clock_gettime fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mtab.c -->
