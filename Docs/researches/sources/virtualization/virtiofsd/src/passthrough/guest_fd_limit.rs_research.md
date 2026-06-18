# File Research: sources/virtualization/virtiofsd/src/passthrough/guest_fd_limit.rs

This file implements a small semaphore for limiting file descriptors allocated on behalf of the guest.

Core types:
- `GuestFdSemaphore`: tracks the initial limit, remaining available slots, and whether exhaustion has already been logged.
- `GuestFile`: wraps a `File` and releases one semaphore slot on drop.

Behavior:
- `GuestFdSemaphore::new(limit)` initializes available slots to the configured limit.
- `allocate()` atomically subtracts one slot with `fetch_update()` and returns a `GuestFile`.
- If no slots remain, it logs one error suggesting `--rlimit-nofile` adjustment and returns `ENFILE`.
- `GuestFile::drop()` calls `release()`, which atomically increments available slots.
- `GuestFile` implements `AsRawFd` and exposes `get_file()` for wrapped file access.

Interactions:
- `PassthroughFs` wraps guest-visible inode and handle FDs in `GuestFile`.
- `HandleDataFile` and `FileOrHandle::File` rely on this wrapper for automatic slot release.

Edge cases and risks:
- Relaxed atomics are sufficient because this semaphore guards counts, not memory visibility of file contents.
- Overflow on release panics, which would indicate an internal accounting bug.
- Returning `ENFILE` is chosen because these errors often go directly back to the guest.
