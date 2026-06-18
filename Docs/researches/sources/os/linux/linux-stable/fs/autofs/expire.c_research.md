# File Research: sources/os/linux/linux-stable/fs/autofs/expire.c

## Purpose
Implements autofs expiry selection and execution for direct, indirect, tree, and leaf mount cases.

## Main Interfaces
- `autofs_expire_wait()`.
- `autofs_expire_run()`.
- `autofs_do_expire_multi()`.
- `autofs_expire_multi()`.
- Internal selection helpers for direct and indirect expiry.

## Important Behavior
Expiry candidates are rejected if pending, too young, busy, a protected autofs submount, or still referenced beyond expected autofs-held counts. The code distinguishes forced expiry, immediate expiry, leaf expiry, direct trigger mounts, tree mounts, symlinks, and indirect mount children.

Candidate selection marks `AUTOFS_INF_WANT_EXPIRE`, synchronizes RCU path walks, rechecks eligibility, then marks `AUTOFS_INF_EXPIRING` and initializes a completion. Completion paths clear both flags, update `last_used` to avoid rapid retry loops, and wake waiters.

`autofs_expire_run()` supports the older ioctl style that copies a single expire packet to userspace. `autofs_do_expire_multi()` sends synchronous daemon notifications via `autofs_wait()`.

## State And Synchronization
Uses `lookup_lock` for dentry traversal/list stability, `fs_lock` for autofs info flags, RCU synchronization before selecting expiring dentries, and completions to coordinate path walkers blocked on expiry.

## Risks / Review Notes
Correctness depends on dentry reference-count conventions and rechecking after RCU synchronization. Expiry behavior differs across direct, indirect, v4 pseudo-direct, and v5 trigger mount layouts.
