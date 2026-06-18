# File Research: sources/os/bsd/netbsd-src/lib/librt/sem.c

Read completely: 435 lines.

Implements POSIX semaphore functions on top of NetBSD `_ksem_*` kernel syscalls. For librt builds, symbols are renamed to `_librt_sem_*` and weak aliases expose the standard `sem_*` names while preserving compatibility with libpthread's copy.

Unnamed non-pshared semaphores allocate a process-local `_sem_st` wrapper containing a kernel semaphore id and magic value. Pshared unnamed semaphores store a specially marked kernel semaphore id directly in `sem_t`, because a heap wrapper would not be shared across processes.

Named semaphores use `_ksem_open()` and a process-local linked list to deduplicate identical kernel ids so repeated opens return the same `sem_t *`. `sem_close()` removes the entry and closes the kernel semaphore; `sem_unlink()` delegates directly. Wait, timedwait, trywait, post, and getvalue are thin wrappers around `_ksem_*`.
