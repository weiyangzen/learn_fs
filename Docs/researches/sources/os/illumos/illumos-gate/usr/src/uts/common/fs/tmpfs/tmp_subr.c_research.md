# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_subr.c

Small tmpfs support routines for access checks, sticky-directory remove policy, kernel-memory accounting, and mount-option parsing.

Key responsibilities:
- Implements `tmp_taccess()` using tmpnode owner/group/mode bits and `secpolicy_vnode_access2()`.
- Implements `tmp_sticky_remove_access()` for sticky directories: removal is allowed for directory owner, entry owner, privileged callers, or writable regular-file entries.
- Implements `tmp_memalloc()` and `tmp_memfree()` with global `tmp_kmemspace` accounting and `tmpfs_maxkmem` enforcement.
- Parses tmpfs size strings in `tmp_convnum()`, supporting bytes, cascading `k/m/g` suffixes, and a single `%` suffix relative to zone swap cap or total available swap.
- Parses root mode mount option strings in `tmp_convmode()` as octal values limited to `07777`.

Dependencies:
- Uses tmpfs globals from `tmp_vfsops.c`: `tmpfs_maxkmem`, `tmp_kmemspace`, and `tmpfs_minfree`.
- Uses zone swap controls, anoninfo accounting, DDI string parsers, policy helpers, and kernel allocator APIs.

Concurrency and locking:
- `tmp_kmemspace` is adjusted atomically on alloc/free.
- The one-per-second over-limit warning in `tmp_memalloc()` uses a static timestamp without a lock, acceptable only as throttled diagnostic state.

Notable risks:
- `musthave` allocations bypass `tmpfs_maxkmem`; callers must keep them subordinate to earlier successful normal allocations.
- `%` size parsing uses pages for intermediate cap calculation to avoid byte overflow.
- Cascading suffix handling is intentional compatibility behavior, not a typo.
