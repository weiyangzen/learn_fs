# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem.h

## Role

Defines the public System V IPC semaphore ABI.

## Key Interfaces

- Permission bits: `SEM_A` for alter and `SEM_R` for read.
- Operation flag: `SEM_UNDO`.
- `semctl()` command constants: `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, and `SETALL`.
- `struct semid_ds` contains IPC permissions, base semaphore pointer, count, operation/change times, binary semaphore marker, and reserved padding.
- `struct sembuf` describes one `semop()` operation.
- Userland prototypes: `semctl()`, `semget()`, `semids()`, `semop()`, and extension `semtimedop()`.

## Compatibility Notes

`struct semid_ds` includes explicit 32-bit padding for future `time_t` expansion while preserving LP64 layout.

## Risk Notes

This is public IPC ABI. Command numbers, structure layout, and time padding are externally visible and must remain compatible with existing binaries.
