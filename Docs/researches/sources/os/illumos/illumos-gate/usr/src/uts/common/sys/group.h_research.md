# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/group.h

## Role

`group.h` defines a small kernel/kmemuser dynamic set abstraction for storing pointer elements and iterating over them.

## Key Interfaces and Data

- Flags `GRP_RESIZE` and `GRP_NORESIZE` control whether insertion can grow capacity.
- `group_t` stores current size, capacity, and a vector of element pointers.
- `group_iter_t` is the iteration cursor type.
- Macros `GROUP_SIZE()` and `GROUP_ACCESS()` expose size and indexed access.
- Functions create/destroy/expand groups, initialize iterators, iterate elements, add/remove elements, empty a group, add/remove at an index, and find an element.
- `group2intlist()` converts group elements to compact integer-list syntax such as `1,2-5,8` using a caller-supplied conversion callback.

## Dependencies and Use

Declarations are only visible for `_KERNEL` or `_KMEMUSER`. Userland without kmem access does not get the abstraction.

## Research Notes

This is a generic pointer-set helper. It does not declare locking; synchronization is the caller's responsibility.
