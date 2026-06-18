# sources/storage-engines/raft-engine/src/env/log_fd/unix.rs

## Purpose
Provides the optimized Unix low-level log file descriptor implementation using raw file descriptors, positional reads/writes, fallocate, and fdatasync/fsync.

## Important APIs, Types, And Functions
`LogFd(RawFd)` exposes `open`, `create`, `close`, `read`, `write`, `truncate`, and `allocate`, and implements `Handle` with `file_size` and `sync`. Helpers include `from_nix_error` and `From<Permission> for OFlag`.

## Control Flow
Open maps engine permissions to `O_RDONLY` or `O_RDWR`, creates files with mode 0644, and has a failpoint path that calls `posix_fadvise64(DONTNEED)`. Reads loop on `pread` until the buffer is full or EOF, retrying `EINTR`. Writes loop on `pwrite`, retrying `EINTR`, mapping `ENOSPC` to a recognizable no-space error. Allocation uses Linux `fallocate` and ignores unsupported-operation errors. Drop closes the fd and logs close errors.

## State And Persistence Behavior
This backend mutates durable file contents at explicit offsets without maintaining a shared seek cursor. `truncate` changes file length, `allocate` may reserve disk blocks, and `sync` uses `fdatasync` on Linux or `fsync` elsewhere.

## Dependencies And Integration Points
Depends on `nix`, `libc` on Linux, failpoints, logging, and `env` traits. It is the default backend for Unix builds unless `std_fs` is enabled.

## Risks And Edge Cases
Short writes returning zero stop the loop without filling the buffer, so upper layers must handle incomplete write results. Sync errors are returned through the handle but some upper layers panic on sync failure. Raw fd ownership relies on `Drop`; accidental duplication would be dangerous.

## Test Signals
Failpoint tests inject no-space, sync, file-size, and close failures. Normal engine tests exercise pread/pwrite, truncate, fallocate, and sync behavior under real temp directories.
