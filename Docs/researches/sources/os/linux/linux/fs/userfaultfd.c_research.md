# File Research: sources/os/linux/linux/fs/userfaultfd.c

## Purpose
Implements Linux `userfaultfd`: a file descriptor API that lets userspace receive and resolve page faults for registered virtual memory ranges, including missing, write-protect, minor, poison, move, fork/remap/remove/unmap events, and optional `/dev/userfaultfd` creation.

## Main Functions
- Fault path:
  - `handle_userfault()`: converts eligible VM faults into `UFFD_EVENT_PAGEFAULT` messages, queues the faulting task, drops the fault lock, wakes poll waiters, and sleeps until userspace resolves or releases the context.
  - `userfaultfd_must_wait()` / `userfaultfd_huge_must_wait()`: recheck page tables after queuing to avoid sleeping on already-resolved faults.
  - `userfault_msg()`: builds the userspace-visible `uffd_msg` with exact/rounded address, write/WP/minor flags, and optional thread id.
- Context/event lifecycle:
  - `userfaultfd_ctx_get()` / `userfaultfd_ctx_put()`: refcount and free `userfaultfd_ctx`.
  - `userfaultfd_release()`: marks context released, unregisters ranges, wakes pending faults/events, and reports hangup.
  - `userfaultfd_event_wait_completion()` / `userfaultfd_event_complete()`: deliver and synchronize non-pagefault events.
- VMA lifecycle hooks:
  - `dup_userfaultfd()`, `dup_userfaultfd_complete()`, `dup_userfaultfd_fail()`: fork handling and `UFFD_EVENT_FORK`.
  - `mremap_userfaultfd_prep()` / `mremap_userfaultfd_complete()` / `mremap_userfaultfd_fail()`: remap event handling.
  - `userfaultfd_remove()`, `userfaultfd_unmap_prep()`, `userfaultfd_unmap_complete()`: remove/unmap event handling.
- File operations:
  - `userfaultfd_poll()`: reports readable pending faults/events and enforces initialized nonblocking use.
  - `userfaultfd_read_iter()` / `userfaultfd_ctx_read()`: read one or more `uffd_msg`s, refile page faults from pending to active queues, and resolve fork events into new fd numbers.
  - `userfaultfd_ioctl()`: dispatches API, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison ioctls.
- Ioctl implementations:
  - `userfaultfd_api()`: negotiates API version, features, and ioctl masks.
  - `userfaultfd_register()` / `userfaultfd_unregister()`: validate ranges, VMA compatibility, hugepage alignment, ownership, and set/clear `VM_UFFD_*` flags.
  - `userfaultfd_copy()`, `userfaultfd_zeropage()`, `userfaultfd_continue()`, `userfaultfd_poison()`, `userfaultfd_move()`: call mm fill/move helpers and optionally wake resolved faults.
  - `userfaultfd_writeprotect()`: toggles UFFD write-protection over a range.
- Creation/init:
  - `new_userfaultfd()`, `SYSCALL_DEFINE1(userfaultfd)`, `userfaultfd_dev_ioctl()`: create contexts via syscall or misc device.
  - `userfaultfd_syscall_allowed()`: enforces `UFFD_USER_MODE_ONLY`, `CAP_SYS_PTRACE`, or sysctl permission.
  - `userfaultfd_init()`: registers `/dev/userfaultfd`, context cache, and `vm.unprivileged_userfaultfd`.

## Important Design Points
- Wait queues are split into pending page faults, active/read page faults, events, and fd poll waiters.
- Wakeups use range filtering and a `refile_seq` seqcount to avoid missing wakeups while faults move between queues.
- `handle_userfault()` is careful about VM fault retry semantics and returns `VM_FAULT_RETRY` with locks released where required.
- `mmap_changing` gates resolving ioctls during fork/remap/remove/unmap windows; callers return `-EAGAIN` or store negative result fields when the mapping is unstable.
- Feature negotiation is one-shot via `cmpxchg(&ctx->features, 0, ctx_features)` and `UFFD_FEATURE_INITIALIZED`.
- `UFFD_FEATURE_WP_ASYNC` implies `UFFD_FEATURE_WP_UNPOPULATED`.
- Fork events need special fd creation in the reader path because creating the new anon inode can sleep.
- HugeTLB has separate page-table checks and registration alignment rules.
- `UFFD_FEATURE_SIGBUS` and `UFFD_USER_MODE_ONLY` can bypass queueing and force normal SIGBUS behavior for disallowed faults.

## Cross-File Relationships
- Relies on mm/userfaultfd infrastructure declared in `include/linux/userfaultfd_k.h` and mm helpers such as `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, `mfill_atomic_poison()`, `mwriteprotect_range()`, and `move_pages()`.
- VMA helpers such as `userfaultfd_register_range()`, `userfaultfd_clear_vma()`, `userfaultfd_release_all()`, and `vma_can_userfault()` are supplied by mm code.
- Exposes syscall behavior to userspace ABI in `include/uapi/linux/userfaultfd.h`.

## Risks / Review Notes
- Lock ordering is delicate: comments explicitly require `fd_wqh.lock` before `fault_pending_wqh.lock`.
- Wait queue entry lifetime relies on careful `list_del()`/`list_del_init()` behavior and stack-allocated wait entries.
- Returning the wrong fault code while a context is released can livelock GUP or cause unintended SIGBUS.
- Range validation must prevent wraparound and invalid page alignment; unaligned source is allowed only where explicitly intended.
- Feature bits and ioctl masks are ABI-sensitive.
