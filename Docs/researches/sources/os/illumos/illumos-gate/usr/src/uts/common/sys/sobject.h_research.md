# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sobject.h

## Role

Defines synchronization object type numbers and the operation vector used by the scheduler/sleep-queue code to reason about owners and priority inheritance.

## Key Contents

Enumerates `SOBJ_NONE`, `SOBJ_MUTEX`, `SOBJ_RWLOCK`, `SOBJ_CV`, `SOBJ_SEMA`, `SOBJ_USER`, `SOBJ_USER_PI`, and `SOBJ_SHUTTLE`. The numeric ordering starts at zero because the synchronization-object mapping array depends on these values.

Defines `sobj_ops_t` with object type, owner lookup, unsleep, and priority-change callbacks.

## Kernel Macros

Under `_KERNEL`, provides dispatch macros for reading object type, finding owner, waking sleepers, and changing inherited/effective priority through the registered operations.
