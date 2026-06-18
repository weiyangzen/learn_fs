# sources/user-network-fs/rclone/lib/mmap/mmap_windows.go

Source read signal: reviewed complete local file (39 lines, sha256 1874f80cc8ef0092).

Purpose: Windows virtual-memory-backed allocator.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` calls `windows.VirtualAlloc` with `MEM_COMMIT` and read/write protection, then constructs a byte slice from the returned pointer. `Free` passes the slice data pointer to `VirtualFree` with `MEM_RELEASE`.

State and persistence behavior: Allocates process virtual memory and releases it explicitly.

Dependencies and integration points: Uses `golang.org/x/sys/windows`, `unsafe`, and `fmt`. Selected by Windows build tag.

Risks and test signals: Unsafe pointer conversion and exact-slice free requirements are critical. Empty slices or derived slices would be unsafe inputs to `Free`.
