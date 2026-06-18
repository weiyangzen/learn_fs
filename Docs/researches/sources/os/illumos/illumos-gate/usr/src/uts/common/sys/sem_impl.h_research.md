# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sem_impl.h

## Role

Defines private System V semaphore implementation structures, semsys subcodes, and ILP32 compatibility layout.

## Key Interfaces

- `semsys()` subcodes: `SEMCTL`, `SEMGET`, `SEMOP`, `SEMIDS`, `SEMTIMEDOP`.
- `ksemid_t` is the kernel semaphore-set descriptor, with `kipc_perm_t`, semaphore array, counts, timestamps, binary flag, maximum operations, and undo-list membership.
- `struct sem` stores value, last operation PID, wait counts, and condition variables for nonzero/zero waiters.
- `struct sem_undo` links per-process undo state by AVL and active undo list, with adjust-on-exit values.
- `struct semid_ds32` is the LP64 kernel view of the ILP32 public structure.
- Kernel exports `semexit()`.

## Risk Notes

Undo tracking and wait counters are core semaphore semantics. The flexible `un_aoe[1]` tail allocation and 32-bit layout must match allocation and copyout logic.
