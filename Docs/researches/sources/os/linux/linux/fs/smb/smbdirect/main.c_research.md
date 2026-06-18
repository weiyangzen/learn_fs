# File Research: sources/os/linux/linux/fs/smb/smbdirect/main.c

Module initialization and teardown for the SMB Direct subsystem.

Key behavior:
- Defines global `smbdirect_globals` with an initialized mutex.
- `smbdirect_module_init()` allocates six named workqueues:
  - `smbdirect-accept`
  - `smbdirect-connect`
  - `smbdirect-idle`
  - `smbdirect-refill`
  - `smbdirect-immediate`
  - `smbdirect-cleanup`
- The refill and immediate queues are high priority; cleanup is high priority and `WQ_MEM_RECLAIM`.
- After workqueues are allocated, it calls `smbdirect_devices_init()` to register the RDMA IB client.
- Failure unwinds already-created workqueues in reverse order and returns the allocation/init error.
- `smbdirect_module_exit()` unregisters devices and destroys all workqueues.

Dependencies:
- Device registration lives in `devices.c`.
- Workqueue pointers are copied into each socket during `smbdirect_socket_init()` in `socket.h`.

Maintenance notes:
- The global mutex serializes module init/exit workqueue and device-list setup.
- Any new per-socket async path should either reuse one of these workqueues or be added here with matching reverse-order failure cleanup.
