# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd_entry.c

## Purpose
This file parses one notifyd database value. A value is a native `notifyd_watcher` followed by zero or more native `notifyd_instance` records.

## Important APIs, Types, and Functions
`notifyd_parse_entry(uint8_t *data, size_t data_len, struct notifyd_watcher *watcher, struct notifyd_instance **instances, size_t *pnum_instances)` is the sole function. It can return the watcher, the instance-array pointer, the number of instances, or just validate/count depending on which output pointers are non-null.

## Control Flow
The parser first requires at least `sizeof(struct notifyd_watcher)`. It copies the watcher by direct struct load if requested. It computes the remaining byte count and requires it to be an exact multiple of `sizeof(struct notifyd_instance)`. It then returns the count and points `instances` at the array inside the original buffer.

## State and Persistence
No state is allocated. The instances pointer aliases the caller-provided buffer, and the caller is responsible for ensuring that buffer remains alive and suitably aligned. The comments explicitly call out alignment concerns.

## Dependencies and Integration Points
It depends on `notifyd_private.h` for the native record structs and `lib/util/debug.h` for logging availability. It is used by notifyd mutation, trigger dispatch, cluster proxy watch setup, peer cleanup, and database walking.

## Risks and Edge Cases
The watcher copy uses direct pointer casting through `uintptr_t`; if dbwrap returns unaligned memory on an architecture that faults on unaligned access, this is sensitive despite the warning comment. The function validates length shape but not semantic fields such as filters, server ids, or pointer validity. Storing `sys_watch` pointers inside values means parsed watcher data from marshalled remote dbs must be sanitized before use, as `notifyd_add_proxy_syswatches()` does.

## Test Signals
There is no direct parser unit test in this group. Existing notifyd tests exercise valid add/remove records. Valuable direct tests would feed too-short buffers, mis-sized instance tails, zero-instance records, and aligned/misaligned buffers.
