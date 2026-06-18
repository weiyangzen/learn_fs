# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_fp.c

## Role

Provides an in-kernel file pointer API for opening, reading, writing, statting, mapping, closing, and shutting down files without necessarily using user-visible file descriptors. It wraps VFS/fileops functionality for kernel consumers that need file-like operations.

## Major Entry Points

- `fp_open()` allocates a file object, sets credentials from the current process when available, performs name lookup with `NLC_LOCKVP`, converts flags with `FFLAGS()`, calls `vn_open()`, and drops the file on failure.
- `fp_vpopen()` converts an already referenced and locked vnode into a file pointer. It rejects symlinks and sockets, validates write/read access, calls `VOP_ACCESS()`, allocates a file object, sets credentials, calls `VOP_OPEN()`, and transfers the vnode reference to the file on success.
- `fp_pread()` and `fp_read()` construct a single-iovec `uio` and call `fo_read()`, supporting explicit offsets for pread and retry/all semantics for full reads.
- `fp_pwrite()` and `fp_write()` mirror the read helpers using `fo_write()`.
- `fp_stat()` calls `fo_stat()`.
- `fp_mmap()` implements descriptor-backed mappings for regular files, character devices, POSIX shared memory, and `/dev/zero`-style anonymous mappings.
- `fp_close()` drops the file reference; `fp_shutdown()` delegates to `fo_shutdown()`.

## VFS/File-System Relevance

- This file is a direct kernel-facing bridge to the VFS layer: `nlookup_init()`, `vn_open()`, `VOP_ACCESS()`, `vn_writechk()`, `VOP_OPEN()`, `VOP_GETATTR_FP()`, vnode type checks, vnode VM objects, and `vm_mmap()` are all used.
- `fp_vpopen()` documents vnode ownership transfer precisely: on success the file pointer inherits the vnode ref and unlocks it; on failure the caller remains responsible for `vput()`.
- `fp_mmap()` validates that the file is `DTYPE_VNODE`, allows only regular files or character devices, derives maximum protections from file flags and vnode attributes, rejects private/copy mappings for character devices, special-cases zero devices to anonymous mappings, and passes the vnode handle to VM.

## Error and Partial I/O Semantics

- Reads/writes reject `nbytes > LONG_MAX`.
- Partial transfer with `ERESTART`, `EINTR`, or `EWOULDBLOCK` is treated as success for pread/pwrite/write; `fp_read(all)` loops until complete, EOF, or unrecoverable error.
- `fp_read(all)` returns `ESPIPE` if it cannot fill the full request despite no direct error.
- Nonblocking `EWOULDBLOCK` is only hidden for partial reads when `all == 0`.

## Research Notes

- This file is useful for kernel subsystems that need to load/store data through VFS without installing descriptors.
- `fp_mmap()` is mostly adapted from the normal mmap path and should be compared with `vm/vm_mmap.c` when researching mmap behavior.
- The API assumes current thread/process credentials in several places; pure kernel thread handling is explicitly noted for `fp_open()`, but `fp_vpopen()` dereferences `td->td_proc->p_ucred`, so callers need process context there.
