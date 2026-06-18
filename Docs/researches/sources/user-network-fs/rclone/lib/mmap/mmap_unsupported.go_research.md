# sources/user-network-fs/rclone/lib/mmap/mmap_unsupported.go

Source read signal: reviewed complete local file (19 lines, sha256 0a2fdd6ba9700579).

Purpose: Fallback allocator for plan9/js where mmap APIs are unavailable.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` returns `make([]byte, size)`; `Free` is a no-op.

State and persistence behavior: Uses Go heap memory and garbage collection; no explicit OS unmap.

Dependencies and integration points: Selected by `plan9 || js` build tag.

Risks and test signals: Memory is not returned synchronously to the OS. Behavior differs from mmap platforms but preserves API shape.
