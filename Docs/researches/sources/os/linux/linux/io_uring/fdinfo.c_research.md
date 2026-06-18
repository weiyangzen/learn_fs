# File Research: sources/os/linux/linux/io_uring/fdinfo.c

## Purpose
Implements `/proc/<pid>/fdinfo` reporting for io_uring file descriptors.

## Main Functions
- `io_uring_show_fdinfo()`: public entry point; tries to lock the ring and emits diagnostic state.
- `__io_uring_show_fdinfo()`: prints SQ/CQ state, visible SQEs/CQEs, SQPOLL thread stats, registered files/buffers, poll list, CQ overflow list, and optional NAPI state.
- NAPI helpers under `CONFIG_NET_RX_BUSY_POLL`: show disabled/dynamic/static tracking and busy-poll settings.

## Important Design Points
- Uses `mutex_trylock(&ctx->uring_lock)` to avoid ABBA deadlock with seq-file locking.
- SQ/CQ observations are intentionally imprecise under concurrent activity.
- Handles SQE128 and mixed SQE layouts, including invalid/corrupt SQE diagnostics.
- CQE32 entries are displayed with extra fields.
- Registered files are displayed through `seq_file_path()`.

## Cross-File Relationships
- Declared in `fdinfo.h`.
- Uses file table helpers, sqpoll state, cancellation table, resource table, opcode names, and NAPI settings.
- Compiled when `CONFIG_PROC_FS` is enabled.

## Risks / Review Notes
- Because it uses trylock, fdinfo may emit nothing if the ring lock is contended.
- It reads user-mutated ring head/tail values and internal cached values without full synchronization for diagnostic purposes.
