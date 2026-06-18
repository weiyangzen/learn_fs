# File Research: sources/os/linux/linux/fs/fs_pin.c

## Purpose
This file implements `fs_pin` list management and teardown. Pins are linked both to a mount and to a superblock/group list so that unmount and group shutdown paths can find and kill outstanding filesystem pins.

## Main Definitions
- Global `pin_lock` protects insertion/removal from the mount and superblock hlist nodes.
- `pin_insert()` links a pin into `m->mnt_sb->s_pins` and `real_mount(m)->mnt_pins`.
- `pin_remove()` unlinks the pin from both lists, marks it done, and wakes waiters.
- `pin_kill()` coordinates first-killer execution of `p->kill(p)` with concurrent waiters.
- `mnt_pin_kill()` repeatedly kills pins linked from one `struct mount`.
- `group_pin_kill()` repeatedly kills pins linked from a superblock/group hlist.

## Control Flow And Behavior
`pin_kill()` is designed to be called while holding RCU read lock around list lookup. If the pin pointer is null, it simply drops RCU. If `done` is zero, the caller transitions it to `-1`, drops locks/RCU, and invokes the pin’s `kill` callback. If another caller is already killing the pin (`done < 0`), the function waits on the pin waitqueue until `pin_remove()` marks completion with `done > 0`.

`mnt_pin_kill()` and `group_pin_kill()` loop until the corresponding hlist head is empty. Each iteration uses `READ_ONCE()` under RCU to fetch the first node and delegates the synchronization protocol to `pin_kill()`.

## Dependencies And Interfaces
The file depends on internal mount structures (`mount.h`) and `struct fs_pin` definitions from VFS internals. It is not exporting symbols here; it is internal VFS lifecycle code.

## Concurrency And Safety
The implementation combines a global spinlock for list structure mutations, per-pin waitqueue locking for state transitions, and RCU for safe lookup while teardown races with removal. The `done` field encodes active kill (`-1`) and completion (`1`).

## Research Notes
The key invariant is single execution of a pin’s `kill` callback while allowing arbitrary concurrent unmount/group teardown callers to converge by waiting for `pin_remove()`.
