# sources/user-network-fs/samba/source3/smbd/smb2_break.c

## Purpose

`smb2_break.c` handles SMB2 oplock and lease break acknowledgements from clients and sends asynchronous oplock/lease break notifications to clients. It converts wire-level SMB2 break packets into Samba oplock or lease state transitions and delegates persistence changes to the oplock and leases database subsystems.

## Important APIs, Types, and Functions

- `smbd_smb2_request_process_break(struct smbd_smb2_request *req)`: entry point for SMB2 BREAK. It first tries the oplock-break packet size and falls back to lease-break parsing when the size matches lease semantics.
- `smbd_smb2_oplock_break_send/recv`: tevent wrapper that maps the client-requested oplock level, removes or downgrades Samba oplock state, and returns the resulting SMB2 oplock level.
- `smbd_smb2_request_process_lease_break(...)`: parses lease key and requested lease state and starts lease downgrade handling.
- `smbd_smb2_lease_break_send/recv`: looks up leased file ids in `leases_db`, calls `downgrade_lease`, and returns the acknowledged lease state.
- `lease_parser(...)` and `struct lease_lookup_state`: callback state for copying file ids out of the leases database.
- `send_break_message_smb2(files_struct *fsp, uint32_t break_from, uint32_t break_to)`: sends server-initiated oplock or lease break notifications.

## Control Flow

Oplock acknowledgements validate the 0x18 request body, read the requested oplock level and file id pair, resolve the FSP with `file_fsp_smb2`, reject closed files or a missing pending break timeout, and require the requested level to be NONE or LEVEL_II. The async send helper creates a fake SMB request, maps SMB2 level to Samba oplock level, and either removes the oplock or downgrades it. Completion builds a 0x18 response body echoing file ids and the resulting oplock level.

Lease acknowledgements validate the 0x24 body, parse the 128-bit lease key and requested lease state, and run a tevent helper. The helper parses the leases database for the client GUID plus lease key, copies associated file ids, rejects missing records, and calls `downgrade_lease`. `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` is treated as a successful acknowledgement path. Completion sends a 0x24 response with the lease key, resulting lease state, zero flags, and zero lease duration.

Server-initiated notifications enter `send_break_message_smb2`. If the open record status is not OK the notification is skipped. Lease oplocks compute whether ACK is required and preserve lease epoch for v2 leases before calling `smbd_smb2_send_lease_break`. Non-lease oplocks map the target break level to SMB2 LEVEL_II or NONE and call `smbd_smb2_send_oplock_break`. Transport send failure disconnects the client.

## State and Persistence Behavior

Client break acknowledgements mutate Samba oplock or lease state through `remove_oplock`, `downgrade_oplock`, and `downgrade_lease`. Lease lookup state is temporary, but the authoritative lease-to-file-id mapping lives in `leases_db`. The FSP's `oplock_timeout`, `sent_oplock_break`, `oplock_type`, `op`, and `lease` fields drive validation and notification behavior. Notifications do not persist new state directly but are part of the state machine that expects later acknowledgements.

## Dependencies and Integration Points

The file integrates with SMB2 request parsing/response helpers, FSP lookup by persistent/volatile file id, Samba oplock mapping helpers, fake SMB request creation, `leases_db`, `downgrade_lease`, `smbd_smb2_send_lease_break`, `smbd_smb2_send_oplock_break`, and client disconnect/error handling. `smb2_server.c` dispatches SMB2 BREAK to this file; `smb2_oplock.c` invokes `send_break_message_smb2`.

## Risks and Edge Cases

The size-based fallback from oplock to lease break must keep wire-structure validation exact; accepting malformed packets could corrupt state or produce wrong errors. Oplock acknowledgements require `oplock_timeout` to be set, so state-machine ordering matters. A failure in `remove_oplock` or `downgrade_oplock` panics as an internal TDB error, making database consistency critical. Lease break handling must map missing lease records to client-visible object-not-found behavior. Notification code must avoid sending breaks for stale or failed open records and must disconnect on transport failure to avoid inconsistent client/server cache state.

## Test Signals

Useful tests include SMB2 oplock acknowledgement to NONE and LEVEL_II, invalid requested levels, closed-file ids, acknowledgements without pending break timeout, lease acknowledgements for existing and missing lease keys, multi-file lease keys, `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` downgrade behavior, v1 versus v2 lease epoch notification fields, ACK-required lease notifications, non-lease oplock notifications, and client disconnect behavior on notification send failure.
