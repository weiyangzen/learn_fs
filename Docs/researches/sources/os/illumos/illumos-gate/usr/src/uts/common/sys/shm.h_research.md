# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm.h

## Role

Defines the public System V shared memory ABI.

## Key Interfaces

- `SHMLBA` is page size in kernel/kmemuser builds and `_sysconf(_SC_PAGESIZE)` in userland.
- Permissions: `SHM_R`, `SHM_W`.
- Attach flags: `SHM_RDONLY`, `SHM_RND`, `SHM_SHARE_MMU`, `SHM_PAGEABLE`.
- `SHMAT_VALID_FLAGS_MASK` lists valid `shmat()` flags.
- `shmatt_t` represents attach counts.
- `struct shmid_ds` contains IPC permissions, segment size, anon-map pointer, lock count, creator/last-operation PIDs, attach counts, timestamps, and reserved padding.
- Control operations: `SHM_LOCK`, `SHM_UNLOCK`.
- Userland prototypes: `shmget()`, `shmids()`, `shmctl()`, `shmat()`, and `shmdt()`.

## Compatibility Notes

The public structure uses LP64 and ILP32 padding branches for pointer visibility and future `time_t` expansion.

## Risk Notes

Shared-memory segment layout and flag values are public ABI. `SHMLBA` must remain a power-of-two low-boundary multiple for address rounding semantics.
