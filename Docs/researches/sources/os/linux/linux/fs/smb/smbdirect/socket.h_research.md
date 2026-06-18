# File Research: sources/os/linux/linux/fs/smb/smbdirect/socket.h

Defines the central SMB Direct socket state object, status enums, logging macros, IO object structs, initialization helper, and small utility functions.

Major contents:
- `enum smbdirect_socket_status` covers lifecycle from `CREATED` through address/route/connect/negotiate states, `CONNECTED`, error/disconnecting/disconnected, and `DESTROYED`.
- `smbdirect_socket_status_string()` converts statuses to diagnostics.
- `SMBDIRECT_DEBUG_ERR_PTR()` safely formats errno values including zero.
- `enum smbdirect_keepalive_status` tracks none/pending/sent keepalive state.
- `struct smbdirect_socket` contains:
  - status and first error.
  - global workqueue pointers and disconnect work.
  - disconnect/destroy krefs.
  - RDMA CM state and expected event.
  - IB PD/CQ/QP/device state.
  - negotiated parameters.
  - connect work/lock.
  - idle keepalive work and timer.
  - listener pending/ready queues and accept-child linkage.
  - send IO pools and batch/local/remote/pending credit counters.
  - receive IO pools, expected PDU type, free list, posted count, receive credits, and reassembly queue.
  - MR lists and ready/used counts.
  - server-side RDMA RW credit state.
  - debug counters and logging callbacks.
- Disabled default work/logging callbacks warn if invoked before proper setup.
- Logging macros route categories such as outgoing, incoming, read, write, RDMA send/recv/event/MR/RW, keepalive, and negotiate through frontend-provided callbacks.
- `smbdirect_socket_init()` zeroes the socket, initializes wait queues/locks/lists/krefs/work items, copies global workqueue pointers, sets default RDMA expected event and poll context, initializes credit counters, and installs disabled logging callbacks.
- Status-check macros centralize expected-state validation and optional cleanup scheduling.
- IO structs:
  - `struct smbdirect_send_io`
  - `struct smbdirect_send_batch`
  - `struct smbdirect_recv_io`
  - `struct smbdirect_mr_io`
  - `struct smbdirect_rw_io`
- `smbdirect_get_buf_page_count()` computes the number of pages spanned by an arbitrary buffer.

Important invariants:
- `SMBDIRECT_SOCKET_CREATED` must remain zero because `smbdirect_socket_init()` relies on `memset()`.
- Work items are initialized to disabled warning callbacks until the appropriate path installs real handlers.
- Send IO supports up to six SGEs: one protocol header plus mapped payload fragments.
- Receive IO currently uses a single SGE covering one large receive buffer.
- The MR kref model allows up to two references: connection ownership and active registration ownership.

Dependencies:
- Includes RDMA RW headers and public SMB Direct parameter/log definitions via `internal.h`.

Maintenance notes:
- This header encodes most subsystem ownership rules. Adding fields usually requires updates in `smbdirect_socket_init()`, cleanup wakeups, destroy paths, and debug reporting.
