# File Research: sources/os/linux/linux-stable/fs/userfaultfd.c

Implements Linux `userfaultfd`, the userspace page-fault handling mechanism exposed through the `userfaultfd(2)` syscall and `/dev/userfaultfd` misc device. It owns `struct userfaultfd_ctx` lifetime, fault/event wait queues, page-fault message creation, ioctl dispatch, VMA registration, wakeups, and integration points used by fork, mremap, unmap, remove, write-protect, minor-fault, poison, and move operations.

Key flows:
- `handle_userfault()` is called from MM fault paths. It validates retry semantics, registers the fault on `fault_pending_wqh`, releases the fault lock, wakes poll waiters, sleeps, and relies on userspace ioctls to resolve or wake the fault.
- `userfaultfd_ctx_read()` moves faults from pending to in-progress queues, returns `uffd_msg` records, and handles event messages such as fork/remap/remove/unmap.
- `userfaultfd_register()` and `userfaultfd_unregister()` validate ranges, VMA compatibility, ownership by one userfaultfd context, hugepage alignment, and update VMA userfault flags through MM helpers.
- `userfaultfd_copy()`, `zeropage()`, `continue()`, `poison()`, `writeprotect()`, and `move()` translate ioctl requests into MM fill/protect/move helpers and optionally wake fault waiters.

Important dependencies are MM VMA helpers, page table inspection, hugetlb handling, `anon_inode`, `miscdevice`, sysctl, LSM capability checks, and UAPI structures from `linux/userfaultfd_k.h`. Concurrency is central: waitqueue locking order, `refile_seq`, memory barriers, ctx refcounts, `mmap_changing`, and `released` all prevent missed wakeups, use-after-free, or lock-held livelocks. Security policy gates kernel-fault-capable userfaultfd use behind `CAP_SYS_PTRACE` or `vm.unprivileged_userfaultfd`; `UFFD_USER_MODE_ONLY` is always allowed.
