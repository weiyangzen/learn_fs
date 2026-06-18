# File Research: sources/os/bsd/openbsd-src/sys/sys/_lock.h

Purpose: Defines common lock metadata structures and flag constants used by OpenBSD synchronization primitives.

Key contents:
- Lock object flags describe class-specific bits, initialization, WITNESS tracking, recursion, sleepability, upgradeability, duplicate acquire allowance, vnode-lock marking, lock class, and parent/child relationship.
- `enum lock_class_index` identifies kernel lock, mutex, rwlock, and recursive rwlock classes.
- `struct lock_object` stores lock type, name, witness metadata, related lock, and flags.
- `struct lock_type` names a lock class.

Filesystem relevance:
- Vnode locks and FUSE node locks use this shared lock metadata for WITNESS and lock-class behavior.
