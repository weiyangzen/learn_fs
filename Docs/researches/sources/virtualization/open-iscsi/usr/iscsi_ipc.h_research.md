# File Research: sources/virtualization/open-iscsi/usr/iscsi_ipc.h

This header defines the user/kernel IPC abstraction used by open-iscsi transports. It is the common interface for netlink/ioctl/control-device implementations to create sessions, manage connections, set parameters, send/receive PDUs, configure networking, and handle firmware/offload features.

Key contents:
- Value type enum: `ISCSI_INT`, `ISCSI_UINT`, `ISCSI_STRING`.
- `struct iscsi_ipc_ev_clbk`, callbacks from IPC layer into initiator/event code:
  - async session create/destroy notifications
  - event context allocation/release
  - event context scheduling
- `ipc_register_ev_callback()` declaration.
- IPC auth modes:
  - UID-only root check
  - legacy UID plus user database matching
- `struct iscsi_ipc`, a function-pointer table for:
  - control device open/close/handle/read/writev
  - SendTargets offload
  - session create/destroy/unbind
  - connection create/destroy/bind/start/stop/state
  - session/host parameter set/get
  - statistics retrieval
  - PDU send/receive transactions
  - net config
  - ping
  - CHAP get/set/delete
  - flashnode create/delete/login/logout/parameter setup
  - host stats

Important dependencies:
- Includes `iscsi_if.h`, the kernel ABI definitions.
- Uses `struct iovec`, `struct sockaddr`, and iSCSI param enums.

Filesystem/storage relevance:
- This is the ABI abstraction through which userspace creates kernel iSCSI sessions that expose remote SCSI LUNs as local block devices. It also carries offload/firmware management operations.

Notable constraints:
- The interface permits POSIX-style errors with `errno` set.
- Some operations are explicitly not implemented yet, such as `get_param`.
- Implementations must handle compatibility across kernels with differing operation support.
