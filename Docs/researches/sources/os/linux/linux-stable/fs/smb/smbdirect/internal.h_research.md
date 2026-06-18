# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/internal.h

## Purpose
Private SMBDirect subsystem header. It defines module-global state, internal device tracking, cleanup scheduling macros, and cross-file prototypes.

## Key Types
- `struct smbdirect_module_state`
  - global mutex
  - workqueues: accept, connect, idle, refill, immediate, cleanup
  - RDMA device list protected by rwlock
- `struct smbdirect_device`
  - global-list node
  - `ib_device *`
  - cached IB device name for remove/rename logs

## Cleanup Macros
- `smbdirect_socket_schedule_cleanup()`
- `smbdirect_socket_schedule_cleanup_lvl()`
- `smbdirect_socket_schedule_cleanup_status()`

These wrap `__smbdirect_socket_schedule_cleanup()` with caller function/line, log level, error, and optional forced status.

## Internal Interfaces
Declares internal functions shared across implementation files:
- socket init/destroy/wait helpers
- RDMA established and negotiation completion
- QP and memory pool lifecycle
- send/recv I/O allocation and posting
- reassembly helpers
- RDMA resource negotiation
- idle timer and credit grant helpers
- MR list lifecycle
- accept-side connect request and negotiate finish
- device subsystem init/exit

## Notes
- Sets `DEFAULT_SYMBOL_NAMESPACE` to `SMBDIRECT`.
- Includes public `<linux/smbdirect.h>` and private `pdu.h`, then includes `socket.h` after globals are declared.
