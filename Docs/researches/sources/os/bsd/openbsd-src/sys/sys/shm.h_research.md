# File Research: sources/os/bsd/openbsd-src/sys/sys/shm.h

System V shared memory public ABI and kernel hooks.

This header defines shared-memory flags for `shmat(2)`, accepted `shmctl(2)` commands, `SHMLBA`, the public `struct shmid_ds`, and BSD-visible `struct shminfo`/`struct shm_sysctl_info`. It also provides `KERN_SHMINFO_*` identifiers and `CTL_KERN_SHMINFO_NAMES` for exposing shared-memory limits and segment data through sysctl.

Kernel builds get global `shminfo`, the `shmsegs` table, and lifecycle hooks for shared-memory initialization, fork inheritance, process exit cleanup, and `sysctl_sysvshm()`. Userland gets the standard `shmat`, `shmctl`, `shmdt`, and `shmget` prototypes.

Filesystem/storage relevance: shared memory is VM-backed rather than filesystem-backed here, but its sysctl accounting and process VM lifecycle interact with the same kernel resource-limit and memory-pressure environment that file-backed mappings use.
