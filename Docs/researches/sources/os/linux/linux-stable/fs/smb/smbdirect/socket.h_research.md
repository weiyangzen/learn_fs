# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.h

## Purpose
Private socket-state definitions for the SMBDirect implementation.

## Status Machine
`enum smbdirect_socket_status` covers:
- creation/listening
- address and route resolution states
- RDMA connect states
- negotiation states
- connected, error, disconnecting, disconnected, destroyed

`smbdirect_socket_status_string()` maps each enum to diagnostics.

## Main Socket Structure
`struct smbdirect_socket` contains:
- status waitqueue and first error
- per-socket workqueue pointers copied from globals
- cleanup/disconnect work
- separate krefs:
  - `disconnect` frontend lifetime
  - `destroy` backend memory lifetime
- RDMA CM state, expected event, and legacy iWARP flag
- IB resources: PD, send/recv CQs, QP, device, poll context
- negotiated `smbdirect_socket_parameters`
- connect work state
- idle keepalive/immediate/timer work
- listener state: pending/ready accepted socket lists, waitqueue, backlog
- accepting-socket backpointer/list node
- send state:
  - mempool/cache
  - batch credit
  - local send WR credits
  - peer-granted send credits
  - pending sends and zero waitqueue
- receive state:
  - expected PDU type
  - mempool/cache
  - free receive buffers
  - posted count/refill work
  - receive credit target/available/count
  - reassembly queue metadata
- MR state:
  - MR type
  - all MR list
  - ready and used counts
- server-side RDMA read/write credits
- debug counters
- logging callbacks

## Initialization Helper
`smbdirect_socket_init()` zeroes the structure and initializes all waitqueues, work items, refs, list heads, locks, defaults, counters, and disabled placeholder work/logging callbacks.

## Logging Helpers
- Fallback logging callbacks warn if used before upper layer installs real callbacks.
- Macros classify logs as outgoing, incoming, read, write, RDMA send/recv/event/MR/RW, keepalive, or negotiate.

## Status Check Macros
- `SMBDIRECT_CHECK_STATUS_WARN()` logs and warns on unexpected state.
- `SMBDIRECT_CHECK_STATUS_DISCONNECT()` also schedules cleanup for unexpected state.

## I/O Types
- `struct smbdirect_send_io`: send CQE, up to 6 SGEs, sibling-chain list, WR, flexible packet header.
- `struct smbdirect_send_batch`: list of sends, WR count, optional remote key invalidation, serialized batch credit.
- `struct smbdirect_recv_io`: receive CQE, single SGE, list node, first-segment marker, flexible packet buffer.
- `enum smbdirect_mr_state` and `struct smbdirect_mr_io`: MR state, refs, mutex, SG table, reg/inv WRs, invalidation completion.
- `struct smbdirect_rw_io`: RDMA read/write context, SG table, completion pointer.
- `smbdirect_get_buf_page_count()` computes page span for arbitrary buffer/length.

## Constants
- RDMA CM retry count: 6
- RNR retry count: 0 because SMBDirect manages credits.
