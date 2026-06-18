# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_subr.c

## Purpose

`kern_subr.c` provides common kernel subroutines for fault-controlled user copies, `uio` data movement, hash table allocation helpers, iovec copyin/free support, and physical-page-backed `uiomove` using lightweight buffers.

## Data Movement APIs

- `copyin_nofault()` and `copyout_nofault()` set `TDF_NOFAULT` around `copyin`/`copyout` so callers can fail instead of taking nontrivial faults.
- `uiomove()` copies between a kernel buffer and a `uio`, supporting `UIO_USERSPACE`, `UIO_SYSSPACE`, and `UIO_NOCOPY`; it updates iovec base/length, residual, and offset, and sets `TDF_DEADLKTREAT` during the transfer.
- `uiomovebp()` wraps `uiomove()` for locked buffers and zero-fills the final partially valid VM page for cached regular-file buffers to avoid recursive buffer-lock faults.
- `uiomove_nofault()` combines `TDF_NOFAULT` with `uiomove()`.
- `uiomovez()` provides zero-fill reads into a `uio`.
- `uiomove_frombuf()` bounds-checks `uio_offset` against a known kernel buffer before moving data.
- `ureadc()` appends one character into the current `uio` iovec.
- `uiomove_fromphys()` maps physical VM pages through `lwbuf` one page at a time and copies to/from a `uio`, reducing ephemeral mapping overhead.

## Hash And Iovec Helpers

- `hashinit()` allocates a power-of-two bucket array and returns `hashmask`.
- `hashdestroy()` asserts all buckets are empty before freeing.
- `hashinit_ext()` allocates a zeroed power-of-two array of caller-sized structures.
- `phashinit()` and `phashinit_ext()` allocate prime-sized bucket/structure arrays from a fixed prime table.
- `iovec_copyin()` copies a user iovec array into either caller-provided small storage or allocated storage, rejects too many iovecs, detects aggregate length overflow, and rejects lengths beyond signed syscall return capacity.

## State And Dependencies

The file exposes `kern.iov_max`, uses thread flags for nofault/deadlock treatment, relies on VM page validity helpers, `lwbuf` mapping, malloc types such as `M_IOV`, and buffer/vnode metadata for `uiomovebp()`.

## Risks And Invariants

For userspace `uio`s, callers must ensure `uio_td` is the current thread. All `uiomove` variants mutate the `uio` in place and must maintain residual/offset consistency on partial errors. Hash destroy assumes callers have already removed entries. `iovec_copyin()` validates aggregate size but leaves semantic checks of user addresses to later copy operations.
