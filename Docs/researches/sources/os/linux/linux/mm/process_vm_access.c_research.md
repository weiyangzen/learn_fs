# File Research: sources/os/linux/linux/mm/process_vm_access.c

## Purpose

`mm/process_vm_access.c` implements the `process_vm_readv(2)` and `process_vm_writev(2)` system calls, allowing one process to copy memory directly to or from another process using local and remote iovec arrays.

## Main Flow

The top-level syscalls call `process_vm_rw()` with `vm_write` false for reads and true for writes.

`process_vm_rw()`:

- Rejects nonzero flags with `-EINVAL`.
- Imports the local iovec through `import_iovec()`, using `ITER_DEST` for read and `ITER_SOURCE` for write.
- Imports remote iovecs with `iovec_from_user()`.
- Calls `process_vm_rw_core()`.
- Frees any heap-allocated iovec arrays.

`process_vm_rw_core()`:

- Calculates the maximum number of remote pages required by any remote vector.
- Uses a small stack array for up to `PVM_MAX_PP_ARRAY_COUNT` page pointers, otherwise kmallocs up to two pages worth of page-pointer storage.
- Looks up the target task with `find_get_task_by_vpid()`.
- Acquires the target mm with `mm_access(task, PTRACE_MODE_ATTACH_REALCREDS)`, mapping `-EACCES` to `-EPERM`.
- Iterates remote iovecs while local iterator space remains.
- Returns bytes copied if any progress was made, otherwise the error code.

`process_vm_rw_single_vec()`:

- Computes the remote page range for one remote iovec.
- Pins remote pages in batches with `pin_user_pages_remote()`, using `FOLL_WRITE` for writes.
- Copies data with `process_vm_rw_pages()`.
- Unpins pages with `unpin_user_pages_dirty_lock()`, marking dirty only for remote writes.

`process_vm_rw_pages()` performs the actual copy page by page via `copy_page_to_iter()` or `copy_page_from_iter()`.

## Error and Partial-Copy Semantics

The code follows syscall semantics where partial progress wins: if any bytes were copied, the syscall returns that byte count even if a later iovec/page faults. If no data was copied, it returns the failure code. Short copy with remaining local iterator data is treated as `-EFAULT`.

## Limits and Allocation Strategy

Remote pages are pinned in bounded batches using `PVM_MAX_USER_PAGES`, derived from two pages of `struct page *` storage. This limits temporary kernel allocation size. A 16-entry stack array avoids heap allocation for small copies.

## Security and Permissions

Access to the remote mm is mediated by `mm_access()` with `PTRACE_MODE_ATTACH_REALCREDS`. The target task reference is held while acquiring the mm, and the mm reference is released with `mmput()`.

## Concurrency and Locking

Remote page pinning takes `mmap_read_lock(mm)` and passes a `locked` pointer to `pin_user_pages_remote()`, which can drop the mmap lock internally. The code unlocks only if the lock remains held. Page dirtying/unpinning is done after copying each batch.

## Filesystem/MM Relevance

The implementation is pure virtual-memory access, but it interacts with filesystem-backed mappings through GUP, page faults, dirty tracking, and writeback semantics. Remote writes to file-backed writable mappings may dirty pages that later flow through filesystem writeback.
