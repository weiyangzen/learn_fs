# File Research: sources/os/linux/linux/mm/madvise.c

Linux `madvise(2)` and `process_madvise(2)` implementation. This file validates advice requests, selects locking strategy, walks VMAs, applies per-behavior memory-management actions, supports anonymous VMA naming, and integrates with KSM, THP, userfaultfd, memory failure, reclaim, swapin, guard PTE markers, and remote process advice.

Key responsibilities:
- Implements `do_madvise()`, `SYSCALL_DEFINE3(madvise)`, vectorized `process_madvise`, and anonymous VMA naming support.
- Defines `struct madvise_behavior` state used across validation, locking, VMA walking, and behavior dispatch.
- Implements VMA flag-changing advice: normal/random/sequential, fork inheritance, wipe/keep-on-fork, core-dump inclusion, KSM mergeability, THP policy, and anonymous VMA names.
- Implements page-state advice: `MADV_WILLNEED`, `MADV_COLD`, `MADV_PAGEOUT`, `MADV_FREE`, `MADV_DONTNEED`, `MADV_DONTNEED_LOCKED`, `MADV_REMOVE`, `MADV_POPULATE_READ`, `MADV_POPULATE_WRITE`, and `MADV_COLLAPSE`.
- Implements guard marker operations: `MADV_GUARD_INSTALL` and `MADV_GUARD_REMOVE`.
- Implements optional memory failure injection: `MADV_HWPOISON` and `MADV_SOFT_OFFLINE`.
- Supports remote process advice through `process_madvise()` with pidfd, ptrace access checks, capability checks, and behavior filtering.

Important behavior:
- `madvise_should_skip()` validates behavior, page alignment, length rounding, and overflow before any locking.
- Lock mode is behavior-dependent: some paths take no mmap lock, some take read or write mmap lock, and some try a per-VMA read lock first.
- Per-VMA read locking is limited to local, single-VMA ranges without userfaultfd and without required `anon_vma_prepare()` under only VMA lock.
- `madvise_walk_vmas()` applies advice across all VMAs in range, reports `-ENOMEM` for gaps while still processing mapped VMAs, and handles paths that temporarily drop the mmap lock.
- `madvise_update_vma()` splits/merges VMAs as needed through VMA modification helpers and updates flags or anonymous VMA name under write mmap lock.
- `MADV_WILLNEED` swaps in anonymous/shmem pages or delegates file readahead to `vfs_fadvise()` after taking a file reference and dropping mmap read lock.
- `MADV_COLD` clears referenced/young state and deactivates eligible LRU folios.
- `MADV_PAGEOUT` isolates eligible folios and calls reclaim, with permission filtering for file-backed pagecache to avoid side channels.
- Large folios and THPs are either handled as whole mappings or split when the advised range only covers part of the folio.
- `MADV_FREE` clears swap entries or marks anonymous folios lazyfree after clearing young/dirty PTE state.
- `MADV_DONTNEED`/`MADV_DONTNEED_LOCKED` zap the target VMA range, with hugetlb alignment adjustments and userfaultfd remove notifications.
- `MADV_REMOVE` validates shared writable file mapping semantics and punches a hole with `vfs_fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`.
- `MADV_POPULATE_READ/WRITE` prefaults page tables using `faultin_page_range()` and maps VM fault results into syscall errors.
- Guard installation sets a VMA guard hint bit, optionally prepares anon_vma, tries to install guard PTE markers, and zaps/retries if populated or huge entries race with the install.
- Guard removal clears only guard PTE markers and permits locked VMAs because it is non-destructive.
- Sealed VMA restrictions block destructive discard operations for read-only anonymous sealed mappings unless the operation is otherwise permitted.
- `process_madvise()` only permits remote `MADV_COLD`, `MADV_PAGEOUT`, `MADV_WILLNEED`, and `MADV_COLLAPSE`, and requires `CAP_SYS_NICE` for remote mm influence.
- Anonymous VMA names are capped at 80 bytes and allow printable ASCII except selected shell/metacharacters.

Dependencies:
- Core MM and VMA APIs: maple/VMA iterators, mmap/VMA locks, VMA modification, page walking, zap, TLB gather, mmu notifiers, folio LRU/reclaim helpers, swap, shmem, hugetlb, THP, KSM, userfaultfd, mseal, and memory policy.
- Filesystem APIs: file references, inode permission checks, `vfs_fadvise()`, `vfs_fallocate()`, and DAX detection.
- Syscall/user APIs: iovec import, pidfd task lookup, ptrace-style mm access, capability checks, and user string duplication.
- Architecture hooks for tagged addresses and VMA access permission.

Notable risks:
- Several behaviors intentionally drop and reacquire mmap locks; callers and loops must tolerate VMA invalidation and range truncation after userfaultfd or filesystem operations.
- Per-VMA read-lock fast paths are limited and require careful fallback to mmap locking for multi-VMA, remote, userfaultfd, or anon-vma-preparation cases.
- Guard installation can return restart semantics after repeated races; vectorized `process_madvise()` cannot safely restart the whole aggregate operation and instead retries internally unless interrupted.
- Pageout for file-backed mappings is permission-filtered to avoid side channels, so behavior differs across anonymous, private file, and shared file mappings.
- Hugetlb `MADV_DONTNEED` rounds the end down to hugepage boundaries to avoid surprising data loss.
- Memory failure injection is privileged and compiled only with `CONFIG_MEMORY_FAILURE`.
- Anonymous VMA naming depends on optional `CONFIG_ANON_VMA_NAME`; without it, setting a name is rejected.
