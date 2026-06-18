# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_sem.c

This file implements NetBSD POSIX semaphores as the loadable `ksem` module. It provides syscall registration, named semaphore lookup, anonymous semaphore file descriptors, process-shared semaphore IDs, fileops for semaphore descriptors, sysctls, and kauth permission checks.

Global state includes `ksem_lock`, a named semaphore list, counts for active named and total semaphores, a process-shared hash table protected by `ksem_pshared_lock`, a kauth listener, and `kern.posix.semmax`/`semcnt` sysctls. `ksem_sysinit()` initializes locks, the pshared hash, authorization listener, sysctls, and syscall package; `ksem_sysfini()` tears them down only if the interface can be removed and no semaphores remain.

Named semaphores use copied-in names with POSIX-style validation: nonempty names must start with `/` and contain no later slash. `do_ksem_open()` preallocates a file descriptor, optionally creates a semaphore, resolves races under `ksem_lock`, honors `O_CREAT`/`O_EXCL`, checks write-style permissions with kauth, inserts new named semaphores, and returns the descriptor-shaped ID. `sys__ksem_unlink()` removes a name, decrements the named count, and either marks the object unlinked until references drain or frees it immediately.

Anonymous semaphores come from `do_ksem_init()`. Newer callers can request `KSEM_PSHARED`, in which case the kernel allocates a random marker-tagged global ID, stores creator process/fd metadata, and inserts the object in the pshared hash. `ksem_get()` resolves either pshared IDs or descriptor IDs, locking and referencing the semaphore and holding any file reference needed for release.

Operations are straightforward but lifetime-sensitive. `sys__ksem_post()` increments up to `SEM_VALUE_MAX` and wakes waiters. `do_ksem_wait()` implements wait, trywait, and timedwait around the semaphore CV, absolute realtime timeouts, signal interruption, and waiter accounting. `sys__ksem_getvalue()` copies out the current value. `sys__ksem_destroy()` is for unnamed semaphores only, rejects waiters, handles pshared creator-only teardown, marks pshared IDs dead before fd close, and then closes the descriptor.

Fileops expose reads of the semaphore name, stat metadata synthesized from semaphore fields, and close semantics. Key risks are refcount/list/hash coordination, pshared ID collision/death handling, fd marker collision avoidance, module unload with live objects, and preserving POSIX semantics across descriptor close versus unlink versus destroy.
