# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_sem.c

## Purpose
Implements POSIX kernel semaphores for FreeBSD, including named semaphore lookup by path, anonymous semaphore descriptors, semaphore wait/post/getvalue/destroy syscalls, descriptor metadata operations, MAC hooks, and 32-bit compatibility wrappers.

## Main Elements
- `struct ksem_mapping`: hash dictionary entry mapping a full jail-rooted path and FNV hash to a referenced `struct ksem`.
- Global state: `ksem_dictionary`, `ksem_dict_lock`, `ksem_count_lock`, `sem_lock`, active count `nsems`, and unload guard `ksem_dead`.
- `ksem_ops`: file operation table for semaphore descriptors; read/write/ioctl/poll/kqueue/truncate are invalid, while stat, close, chmod, chown, kinfo, comparison, and descriptor passing are supported.
- Object lifetime: `ksem_alloc()`, `ksem_hold()`, and `ksem_drop()` allocate semaphore state, initialize condition variables and MAC labels, enforce POSIX semaphore count limits, and free on last reference.
- Dictionary operations: `ksem_lookup()`, `ksem_insert()`, and `ksem_remove()` implement named semaphore creation/open/unlink with permission and MAC checks.
- Creation path: `ksem_create()` handles file descriptor allocation, early semid copyout, anonymous vs named objects, jail path prefixing, `O_CREAT`/`O_EXCL`, mode masking, and reference transfer into `finit()`.
- Syscalls: `ksem_init`, `ksem_open`, `ksem_unlink`, `ksem_close`, `ksem_post`, `ksem_wait`, `ksem_timedwait`, `ksem_trywait`, `ksem_getvalue`, and `ksem_destroy`.
- Wait implementation: `kern_sem_wait()` handles trywait, interruptible indefinite waits, absolute timed waits, wait counters, value decrement, and MAC wait checks under `sem_lock`.
- Module setup: registers POSIX.1b semaphore feature values, syscall helpers, 32-bit syscall helpers, hash table, and locks; unload is rejected while semaphores remain active.

## Dependencies And Integration
Uses the file descriptor layer, Capsicum semaphore rights (`CAP_SEM_POST`, `CAP_SEM_WAIT`, `CAP_SEM_GETVALUE`), POSIX.1b configuration, FNV hashing, jail-root path rewriting, MAC framework hooks, condition variables, audit, resource counters, and syscall helper registration.

## Risk Notes
The implementation uses one global `sem_lock` for semaphore value/waiter/metadata operations, so behavior is simple but contended. `ksem_create()` copies the descriptor id to user memory before final object creation to simplify rollback, so later errors must close/drop the provisional fd correctly. Named semaphore unlink removes the dictionary reference while open descriptors continue holding object references. Anonymous semaphores can only be destroyed through `ksem_destroy()` and reject `ksem_close()`.
