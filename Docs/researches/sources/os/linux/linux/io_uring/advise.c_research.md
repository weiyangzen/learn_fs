# File Research: sources/os/linux/linux/io_uring/advise.c

## Purpose
Implements io_uring `madvise` and `fadvise` opcodes.

## Main Functions
- `io_madvise_prep()`: validates unused SQE fields, extracts address/length/advice, and forces async execution when advice syscalls and MMU are available.
- `io_madvise()`: calls `do_madvise()` and completes the request.
- `io_fadvise_force_async()`: identifies fadvise modes that must run asynchronously.
- `io_fadvise_prep()`: validates SQE fields and extracts offset/length/advice.
- `io_fadvise()`: calls `vfs_fadvise()` on `req->file`, marks failed requests, and completes.

## Important Design Points
- `madvise` support is gated by `CONFIG_ADVISE_SYSCALLS` and `CONFIG_MMU`; otherwise prep/issue returns `-EOPNOTSUPP`.
- `madvise` is always forced async because it works on `current->mm`.
- `fadvise` only forces async for advice values outside normal/random/sequential.
- Both operations reject `buf_index` and `splice_fd_in`.

## Cross-File Relationships
- Uses `vfs_fadvise()` declared in `fs.h`.
- Operation prototypes are declared in `advise.h` and wired through io_uring opcode definitions elsewhere.

## Risks / Review Notes
- `sqe->off`, `sqe->addr`, and `sqe->len` carry different meanings between `madvise` and `fadvise`; opcode prep must remain aligned with the userspace ABI.
- `io_fadvise()` warns if forced-async advice reaches nonblocking issue context.
