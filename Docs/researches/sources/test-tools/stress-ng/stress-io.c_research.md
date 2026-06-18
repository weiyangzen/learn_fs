# sources/test-tools/stress-ng/stress-io.c

## Purpose
`stress-io.c` is stress-ng's legacy sync I/O stressor. It repeatedly writes to a temp file, calls `fsync`, `fdatasync`, global `sync`, and `syncfs` on the current directory and discovered mount points.

## Important APIs, Types, And Functions
`stess_io_write()` writes a random 32-bit value at offset zero when `syncfs` support is compiled. `stress_io()` creates a temp directory/file, unlinks the file while keeping it open, hints short file I/O, discovers mount points via `stress_mount_get()`, opens directory fds for each mount, and loops through sync operations. It uses a bad fd from `stress_fs_bad_fd_get()` to verify `syncfs` failure behavior.

## Control Flow
With `HAVE_SYNCFS`, setup creates a temp file and opens mount directories. After sync barrier, each iteration writes random data, alternates fsync/fdatasync ordering, calls global `shim_sync()`, writes again, calls `syncfs()` on the current directory and each mount fd, tolerates selected mount errors, checks that `syncfs` on a bad fd does not succeed, and increments bogo ops. Cleanup closes directory/mount/temp fds, frees mount strings, and removes the temp directory.

## State And Persistence
The temp file is unlinked after opening and removed with the temp directory. The stressor intentionally flushes system and filesystem state, affecting the host's I/O writeback behavior while running.

## Dependencies And Integration Points
It depends on stress-ng filesystem and mount helpers, `syncfs` when available, `shim_sync`, fd cleanup helpers, process state/sync, and verify-always registration.

## Risks
Global `sync()` and per-mount `syncfs()` can impose heavy host-wide I/O latency. Mount discovery may include filesystems where syncfs returns quota/space/interruption errors, which are tolerated. If `syncfs` is unavailable at runtime (`ENOSYS`), the loop still counts bogo ops.

## Test Signals
Signals include the legacy warning on instance zero, clean temp directory removal, bad-fd `syncfs` failure, tolerated mount errors, fd cleanup for all discovered mounts, and bogo count progress.
