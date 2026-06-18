# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_panic.h

## Role

Defines UFS fix-on-panic/failure state tracking used when UFS detects internal inconsistency and applies configured on-error behavior.

## Key Types

- `ufs_failure_states_t` is a bit-valued state machine:
  - initial: `UF_UNDEF`, `UF_INIT`, `UF_QUEUE`
  - transitional: `UF_TRYLCK`, `UF_LOCKED`, `UF_UMOUNT`, `UF_FIXING`
  - terminal/near-terminal: `UF_FIXED`, `UF_NOTFIX`, `UF_REPLICA`, `UF_PANIC`
  - helpers: `UF_ILLEGAL`, `UF_ALLSTATES`
- `ufs_failure_t` records one failure manifestation with queue links, duplicate/master pointers, superblock buffer, VFS/ufsvfs references, device, state, timestamps, lockfs request, retry/counter, mutex, saved filesystem name, and original panic string.
- `vfs_ufsfx_t` stores per-filesystem fix-on-panic flags and current failure pointer.

## Interfaces

Kernel prototypes include `ufs_fault()`, global/per-mount init and teardown, lockfs coordination, unlock coordination, and failure queue length query. Exports global `ufs_fix` queue.

## Risk Notes

This file sits on the path from metadata inconsistency to panic, lockfs, unmount, or repair. State transitions and saved post-unmount references must avoid use-after-free while still identifying the failed filesystem.
