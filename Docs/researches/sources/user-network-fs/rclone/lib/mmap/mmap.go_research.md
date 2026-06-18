# sources/user-network-fs/rclone/lib/mmap/mmap.go

Source read signal: reviewed complete local file (30 lines, sha256 b26994cae6e55e7a).

Purpose: Provides shared helpers around platform-specific large memory allocation.

Important APIs/types/functions: Exports `PageSize`, `MustAlloc`, and `MustFree`.

Control flow: `MustAlloc` calls `Alloc` and panics on error. `MustFree` calls `Free` and panics on error.

State and persistence behavior: Allocates process memory only. Callers must pass the exact returned slice to free on mmap-backed platforms.

Dependencies and integration points: Uses `os.Getpagesize`; platform files provide `Alloc`/`Free`. Used by high-throughput buffers that benefit from OS-backed allocation.

Risks and test signals: Panic helpers are only safe where allocation failure is unrecoverable. Derived slices passed to `Free` can fail or unmap the wrong range; tests cover basic write/free.
