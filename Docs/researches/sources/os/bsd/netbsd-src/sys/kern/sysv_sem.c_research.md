# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_sem.c

## Purpose

`sysv_sem.c` implements NetBSD's System V semaphore sets: allocation, control operations, vectorized atomic semaphore operations, timed waits, SEM_UNDO process cleanup, and runtime resizing of semaphore limits.

## Main Responsibilities

- Initializes and tears down semaphore identifiers, semaphore storage, wait condition variables, and undo records.
- Implements `semget`, `semctl`, `semop`, and `semtimedop`.
- Maintains per-process undo vectors and applies them at process exit.
- Supports dynamic resizing of `semmni`, `semmns`, and `semmnu`.
- Registers an exit hook lazily when semaphore syscalls are used.

## Core Data Model

The subsystem uses one wired memory block split into:

- `sema`: array of `struct semid_ds` semaphore-set descriptors.
- `sem`: packed array of individual `struct __sem` objects.
- `semcv`: one condition variable per semaphore set.
- `semu`: fixed-size pool of process undo vectors.

`semtot` tracks the number of live semaphores in the packed `sem` array. Removing a set compacts later semaphores and adjusts `_sem_base` pointers in other descriptors.

## Semaphore Operations

`semget()` finds an existing set by key or allocates a new one if requested, enforcing per-set and global semaphore limits.

`semctl1()` implements descriptor metadata operations plus `GETVAL`, `GETALL`, `SETVAL`, `SETALL`, `GETPID`, `GETNCNT`, and `GETZCNT`. Set/remove/value mutations clear affected SEM_UNDO entries and wake sleepers.

`do_semop1()` applies a vector of operations atomically. It rolls back partial changes if any operation cannot proceed, waits on the set condition variable unless `IPC_NOWAIT` applies, updates wait counters, supports timeouts, and translates timeout/interruption errors. SEM_UNDO adjustments are applied only after the vector succeeds; failures while adding undo records roll back both undo state and semaphore values.

## Process Exit

`semexit()` scans the global undo list for the exiting process, applies each stored adjustment to surviving semaphore sets, clamps negative underflow to zero, wakes affected waiters, and removes the undo vector.

## Concurrency Notes

`semlock` protects all semaphore state. `sem_realloc_state`, `sem_waiters`, and `sem_realloc_cv` coordinate resizing with blocked `semop` callers. `RUN_ONCE` protects lazy installation of the exit hook.
