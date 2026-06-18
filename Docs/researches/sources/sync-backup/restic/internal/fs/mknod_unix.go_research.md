# sources/sync-backup/restic/internal/fs/mknod_unix.go

Purpose: Generic Unix `mknod` implementation for non-FreeBSD, non-Windows platforms.

Important APIs: `mknod`.

Control flow and state: Calls `unix.Mknod(path, mode, int(dev))` and wraps failures as `*os.PathError` with operation `"mknod"`.

Dependencies and integration: Used by `NodeCreateAt` to create block devices, character devices, and FIFOs via `mkfifo`.

Risks: Device creation usually requires elevated privileges. Device number conversion to `int` relies on platform size compatibility.

Test signals: `node_unix_test.go` verifies error wrapping through `mkfifo`; restore tests cover FIFO creation when supported.
