# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_rctl.h

This header defines resource-control quantity storage for System V IPC.

Key definition:
- `ipc_rqty_t` stores:
  - `ipcq_shmmni`
  - `ipcq_semmni`
  - `ipcq_msgmni`

Notes:
- Comments state these quantities are protected by the corresponding IPC service lock.
- Used by `ipc_impl.h` accounting macros through project/zone IPC data.

Dependencies:
- Includes `sys/rctl.h`.

Relevance:
- Resource-control support for IPC object counts.
