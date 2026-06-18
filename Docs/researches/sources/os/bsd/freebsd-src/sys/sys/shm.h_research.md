# File Research: sources/os/bsd/freebsd-src/sys/sys/shm.h

System V shared memory ABI and kernel-private state.

Key responsibilities:
- Defines shared memory attach flags `SHM_RDONLY`, `SHM_RND`, `SHM_REMAP`, and `SHMLBA`.
- Defines public permission aliases, `shmctl()` commands, and Linux-compatible `SHM_STAT`/`SHM_INFO`.
- Defines `shmid_ds`, compatibility `shmid_ds_old`, `shmatt_t`, and Linux-style `shm_info`.
- Under kernel/internal visibility, defines `shminfo` and `shmid_kernel`.
- Declares userspace `shmat()`, `shmget()`, `shmctl()`, and `shmdt()`.

Important patterns:
- Kernel metadata is stored in `shmid_kernel`, pairing the public descriptor with a VM object, MAC label, and creator credentials.
- Segment state flags distinguish free, removed, and allocated entries.
- Compatibility structures preserve older integer-sized segment and attach-count ABI.

Research relevance:
- Connects SysV IPC semantics with VM objects and per-process VM space lifecycle hooks.
