# sources/test-tools/strace/src/ipc_shmctl.c

Purpose: mpers-aware decoder for `shmctl` shared-memory control commands.

Important APIs/types/functions: `SYS_FUNC(shmctl)`, `print_ipc_perm`, `print_shmid_ds`, `print_ipc_info`, `print_shm_info`, `shmid_ds_t`, `struct_shm_info_t`, `struct_shm_ipc_info_t`, `DEF_MPERS_TYPE`, and `shmctl_flags`.

Control flow: the decoder picks the buffer argument for direct or indirect IPC, strips `IPC_64` for dispatch, and prints `shmid` plus command on entry. `IPC_SET` decodes `shmid_ds` immediately; status and info commands defer to exit; unknown commands print the buffer address. Exit decodes `shmid_ds`, IPC limits, or runtime shared-memory info depending on command.

State and persistence behavior: no explicit private state; the buffer address is derived from syscall arguments on both phases. Reads only tracee memory structures.

Dependencies and integration points: relies on `ipc_defs.h`, mpers structure sizing, PID-aware field printers for creator/last PID fields, and shared-memory xlat tables.

Risks: old compat IPC is not fully decoded. `IPC_SET` intentionally omits read-only status fields. Kernel/libc structure differences are handled only if configure/mpers probes are correct.

Test signals: cover `IPC_SET`, `IPC_STAT`, `SHM_STAT`, `SHM_STAT_ANY`, `IPC_INFO`, `SHM_INFO`, inaccessible buffers, PID field formatting, and compat layout variants.
