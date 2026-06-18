# File Research: sources/os/linux/linux-stable/fs/fs_pin.c

## Purpose
Provides infrastructure for pinning filesystem or mount resources and safely killing those pins during unmount or group teardown.

## Key Interfaces
- `pin_insert()` links a `struct fs_pin` into both superblock and mount pin lists.
- `pin_remove()` unlinks a pin, marks it done, and wakes waiters.
- `pin_kill()` coordinates one caller running the pin-specific kill callback while other contenders wait.
- `mnt_pin_kill()` drains all pins attached to a mount.
- `group_pin_kill()` drains all pins attached to a shared hlist, typically superblock-scoped.

## Design Notes
A global `pin_lock` protects list membership. Each pin also has its own waitqueue lock and `done` state:
- `0` means live.
- `-1` means kill in progress.
- positive means removed/completed.

`pin_kill()` is designed to be called while holding RCU read lock; it drops and reacquires RCU around blocking or callback paths.

## Dependencies
Uses VFS mount internals from `mount.h`, `struct fs_pin` from VFS internal headers, spinlocks, hlist operations, RCU, and wait queues.

## Research Notes
This is small but concurrency-sensitive teardown code. The important invariant is that list removal and waitqueue completion must make later drain loops stop without freeing memory while another killer is still waiting.
