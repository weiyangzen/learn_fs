# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/shm_impl.h

## Role

Defines private System V shared-memory implementation structures, syscall subcodes, and 32-bit compatibility layout.

## Key Interfaces

- `shmsys()` subcodes: `SHMAT`, `SHMCTL`, `SHMDT`, `SHMGET`, `SHMIDS`.
- `kshmid_t` is the kernel segment descriptor with permissions, segment size, anon map, lock counts, lock mutex, PIDs, ISM attach count, timestamps, shared page table info, and legacy reserved field.
- `SHMSA_ISM` marks shared page table usage in segment accounting.
- `sptinfo_t` references a dummy address space for ISM segment handling.
- `segacct_t`, protected by `p_lock`, records per-process attached segment accounting in an AVL tree.
- Error codes `SHMID_NONE` and `SHMID_FREE` are used by `shmgetid()`.
- Kernel functions: `shminit()`, `shmfork()`, `shmexit()`, `shmgetid()`.
- `struct shmid_ds32` is the ILP32 public layout for LP64 kernels.

## Risk Notes

ISM/shared-page-table fields and per-process `segacct_t` state are sensitive to fork/exit/detach behavior. 32-bit layout must match copyin/copyout translation.
