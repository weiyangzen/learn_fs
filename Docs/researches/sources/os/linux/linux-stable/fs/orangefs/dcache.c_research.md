# File Research: sources/os/linux/linux-stable/fs/orangefs/dcache.c

## Scope

This file implements OrangeFS dentry revalidation.

## APIs Covered

- `orangefs_revalidate_lookup()` reissues a no-follow lookup to validate positive and negative dentries.
- `orangefs_d_revalidate()` checks dentry timeout, handles RCU constraints, validates root dentries, and refreshes inode state.
- Exports `orangefs_dentry_operations` with `.d_revalidate`.

## Control Flow And Behavior

- Dentries are trusted until their `d_fsdata` timeout expires.
- RCU pathwalk revalidation returns `-ECHILD` after timeout.
- Positive dentries are dropped if lookup fails or returns a different handle.
- Negative dentries are kept only if lookup still returns `-ENOENT`.
- Positive dentries that pass lookup are further checked with `orangefs_inode_check_changed()`.

## Risks And Invariants

- Root handle dentries bypass network revalidation.
- Revalidation depends on OrangeFS object handles, not inode numbers, for identity.
- Timeout refresh is centralized through `orangefs_set_timeout()`.
