# sources/user-network-fs/rclone/lib/mmap/mmap_unix.go

Source read signal: reviewed complete local file (34 lines, sha256 670f0339d3b31899).

Purpose: Unix mmap-backed allocator for non-Plan9, non-Windows, non-JS builds.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` calls anonymous private `unix.Mmap` with read/write permissions; `Free` calls `unix.Munmap` and wraps failures.

State and persistence behavior: Allocates anonymous virtual memory and releases it on `Free`; no file persistence.

Dependencies and integration points: Uses `golang.org/x/sys/unix` and `fmt`. Selected by build tags for Unix-like systems.

Risks and test signals: Callers must free the exact slice. Very large allocations may reserve address space or fail depending on OS overcommit policy.
