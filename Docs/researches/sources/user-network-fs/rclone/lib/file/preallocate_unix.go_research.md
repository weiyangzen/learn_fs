# sources/user-network-fs/rclone/lib/file/preallocate_unix.go

Source read signal: reviewed complete local file (72 lines, sha256 7328c813fd20ab2e).

Purpose: Linux implementation of file preallocation through `fallocate`.

Important APIs/types/functions: Exports `PreallocateImplemented=true`, `PreAllocate`, `SetSparseImplemented=false`, and `SetSparse`. Package state includes candidate `fallocFlags`, atomic `fallocFlagsIndex`, and `preAllocateMu`.

Control flow: `PreAllocate` ignores non-positive sizes, serializes calls, tries the current `fallocate` flag combination, advances to the next combination on `ENOTSUP`, maps `ENOSPC` to `ErrDiskFull`, retries on `EINTR`, and eventually returns nil if all fallocate modes are disabled.

State and persistence behavior: May allocate disk blocks for the file. The atomic flag index persists for the process after discovering unsupported fallocate modes.

Dependencies and integration points: Uses `golang.org/x/sys/unix`, `syscall`, `sync`, `atomic`, and `fs.Debugf`. Integrates with transfer writers that preallocate destination files.

Risks and test signals: Global fallback state means one filesystem's `ENOTSUP` can affect later files. Mutex limits concurrency. Disk-full mapping is important for retry/fatal policy; ZFS hole-punch fallback is noted in comments.
