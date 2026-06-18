# File Research: sources/os/bsd/dragonflybsd/sys/sys/shm.h

This header defines System V shared memory ABI structures, flags, tunables, and kernel/user APIs.

Key responsibilities:
- Defines attach flags:
  - `SHM_RDONLY`
  - `SHM_RND`
  - `SHMLBA`
- Under BSD visibility, defines `SHM_R` and `SHM_W`.
- Defines `shmatt_t`, plus `pid_t`, `size_t`, and `time_t` if needed.
- Defines public `struct shmid_ds`:
  - IPC permissions
  - segment size
  - last-op and creator PIDs
  - attach count
  - attach/detach/change times
  - internal pointer
- Defines kernel `struct shminfo` with SysV shared memory limits.
- Declares kernel `shminfo`, `shmexit()`, and `shmfork()`.
- Declares userland `shmget()`, `shmctl()`, `shmat()`, and `shmdt()`.

Important invariants:
- `SHMLBA` is `PAGE_SIZE`.
- Shared memory accounting tracks both creator and last-operation process IDs.
- Kernel VM integration is explicit through `struct vmspace` in `shmexit()`.

Research notes:
- This is the System V shared memory ABI plus process/VM lifecycle hooks.
