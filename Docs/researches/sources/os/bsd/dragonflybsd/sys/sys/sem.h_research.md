# File Research: sources/os/bsd/dragonflybsd/sys/sys/sem.h

This header defines System V semaphore ABI structures, commands, permissions, kernel metadata, and syscall declarations.

Key responsibilities:
- Includes IPC and machine integer types.
- Defines `pid_t`, `size_t`, and `time_t` if needed.
- Defines public `struct semid_ds`:
  - permission record
  - base semaphore pointer
  - semaphore count
  - operation/change timestamps
  - SV ABI padding fields
- Defines kernel `struct semid_pool` containing a lock, descriptor, and generation number.
- Defines `struct sembuf` for `semop()` operations and `SEM_UNDO`.
- Under BSD visibility:
  - defines `MAX_SOPS`
  - defines `union semun`
  - defines `SEM_STAT`, `SEM_A`, and `SEM_R`
- Defines `semctl()` command constants:
  - `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, `SETALL`
- Defines kernel `struct seminfo` for semaphore limits/tunables.
- Defines internal `SEM_ALLOC` and `SEM_DEST` mode bits.
- Declares kernel `semexit()` and global `seminfo`.
- Declares userland `semctl()`, `semget()`, and `semop()`.

Important invariants:
- The ABI preserves historical SV ABI padding in `struct semid_ds`.
- `union semun` is BSD-visible rather than always exposed.
- `SEM_DEST` marks a semaphore set being destroyed on last detach.

Research notes:
- This is the public and kernel-facing System V semaphore contract.
