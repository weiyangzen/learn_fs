# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kdoor.c

## Role

Implements kernel-to-user-space SMB door upcalls used by the SMB server for operations such as DFS referral queries.

## Major Responsibilities

- Maintains the server door handle, door id, active call count, mutex, and close condition variable.
- Opens and closes kernel door handles safely.
- Prevents door close while upcalls are active.
- Encodes request headers and request bodies with XDR.
- Supports synchronous upcalls and asynchronous request/response upcall pairs.
- Retries door upcalls on transient `EAGAIN`/`EINTR`.
- Validates response headers, magic, opcode, transaction id, and door return code.
- Frees request and response buffers, including doorfs-grown result buffers.

## Key Functions

- `smb_kdoor_init()` and `smb_kdoor_fini()` initialize and destroy door synchronization state.
- `smb_kdoor_open()` closes any existing handle and looks up the new door id.
- `smb_kdoor_close()` waits for active calls to drain, releases the door handle, and resets state.
- `smb_kdoor_upcall()` prepares an `smb_doorarg_t`, creates an event, accounts for active calls, and runs synchronous or async call flow.
- `smb_kdoor_send()` sends the request half of an async door operation.
- `smb_kdoor_receive()` requests the async response using `SMB_DR_ASYNC_RESPONSE`.
- `smb_kdoor_upcall_private()` performs the limited kernel door upcall with retry and stopping checks.
- `smb_kdoor_encode()` computes XDR size, builds the SMB door header, and encodes request payload.
- `smb_kdoor_decode()` decodes and validates the response header and response payload.
- `smb_kdoor_sethdr()` fills SMB door header fields.
- `smb_kdoor_chkhdr()` validates response identity and door return status.
- `smb_kdoor_free()` frees both argument and result buffers.

## Research Notes

The function copies `door_arg_t` before upcall because doorfs may replace `data_ptr`; response data is therefore consumed via `rbuf`/`rsize`. Async upcalls are modeled as send plus later receive, keyed by the SMB event transaction id.
