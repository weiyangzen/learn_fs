# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_futex.c

Implements OpenBSD’s futex syscall support with wait, wake, and requeue operations over hashed sleep queues. Futex identity is derived either from the private process plus address or from shared UVM backing object/amap plus offset.

`struct futex` represents one waiting thread on one user address. It stores current sleep queue, list entry, private process key, UVM object/amap/offset key, and volatile waiting `struct proc *`. A futex is considered waiting while `ft_proc` is non-NULL. Wakeup-side ownership of list references ends when the sleep-queue lock holder clears `ft_proc`.

`futex_init()` initializes 64 cacheline-aligned `futex_slpque` buckets, each with a TAILQ, rwlock, and randomized `fsq_id` low bits preserving bucket order for deadlock-free double locking.

`sys_futex()` dispatches by `FUTEX_OP_MASK`: `FUTEX_WAIT`, `FUTEX_WAKE`, and `FUTEX_REQUEUE`; unknown ops return `ENOSYS`.

`futex_addrs()` computes the futex key. Private futexes use `p->p_p`; shared futexes inspect the process VM map and, only for shared-inherited mappings, key on backing `uvm_object` plus offset or amap plus page offset. Otherwise they fall back to raw virtual offset with no shared object key.

`futex_wait()` validates optional relative timeout, initializes a stack-local `struct futex`, inserts it into the hashed sleep queue before reading user memory, then `copyin32()` checks the current value. If the value differs it returns `EAGAIN`; if timeout is zero it returns `ETIMEDOUT`. It sleeps with `sleep_setup()`/`sleep_finish()` while requiring that the futex be removed from the queue before returning. Timeout/restart results are translated to `ETIMEDOUT`/`ECANCELED`.

`futex_wake()` builds a key, locks the bucket, removes up to `n` matching waiters into a temporary list, wakes them via `futex_list_wakeup()`, and returns the count. Wakeup clears `ft_proc` under scheduler lock and calls `wakeup_proc()`.

`futex_requeue()` wakes up to `n` waiters from one futex and requeues up to `m` remaining waiters to another futex. It locks old/new buckets by `fsq_id` order, handles same-bucket requeue, updates each moved futex’s queue pointer and key fields, and returns the number woken.

Filesystem relevance: not filesystem-specific. It is a synchronization primitive used by user processes; its UVM mapping key logic matters for shared memory backed by files or objects, but it does not itself perform VFS operations.
