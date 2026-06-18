# sources/user-network-fs/samba/source4/smb_server/smb/request.c

## Purpose
Implements `struct smbsrv_request` lifecycle and low-level SMB1 packet utilities: request allocation/destruction, reply buffer construction/growth, signing-aware send, error serialization, string/blob parsing and writing, bounds checking, and SMB file handle mapping.

## Important APIs, Types, And Functions
- `smbsrv_init_request()` allocates a request under the connection and installs a destructor that unlinks it from `smb_conn->requests`.
- `smbsrv_setup_reply()` and `req_setup_chain_reply()` build normal and chained reply buffers and initialize SMB headers, VWV/data pointers, flags, IDs, and BCC.
- `req_grow_data()` and `req_grow_allocation()` resize output buffers while preserving internal pointers.
- `smbsrv_send_reply()` signs and sends; `smbsrv_send_reply_nosign()` sends manually constructed or negotiation/raw packets.
- `smbsrv_setup_error()` maps NTSTATUS to NT or DOS error encoding based on negotiated support.
- `req_push_str()`, `req_append_bytes()`, `req_append_var_block()`, `req_pull_string()`, `req_pull_ascii4()`, `req_pull_blob()`, and `req_data_oob()` are the primary wire buffer helpers.
- `smbsrv_pull_fnum()`, `smbsrv_push_fnum()`, and handle callback functions map 16-bit SMB FIDs to NTVFS handles.

## Control Flow
Receive code initializes request input pointers, then calls `smbsrv_setup_bufinfo()` so string/blob helpers know the active data range and Unicode mode. Reply handlers allocate output with the needed word count and initial data size; append/grow helpers update BCC and total packet size. Sending writes the NBT length, queues the packet through `packet_send()`, and frees the request. Error sending constructs a zero-word reply and then serializes status. Handle creation is two-phase: allocate a frontend handle and NTVFS handle during backend open, then make it valid only after backend success.

## State And Persistence
Request objects are talloc-owned and usually freed after send; async NTVFS requests steal them under the tcon backend context until completion. Output pointer fields must always track reallocations. `request_bufinfo` holds per-request parsing state. Valid SMB handles persist under the tcon after `smbsrv_handle_make_valid()` steals the handle away from the request. Handle lookup enforces that the opening session matches the current request session.

## Dependencies And Integration Points
Used by all SMB1 handlers and transaction code. It depends on packet streaming, NTVFS handle callbacks, Samba charset conversion, DOS/NT status mapping, signing, and talloc memory ownership. The callback functions are registered in `service.c` during tree connection setup.

## Risks
Buffer growth uses size deltas and panics if a normal reply exceeds negotiated max transmit unless `SMBSRV_REQ_CONTROL_LARGE` is set. String conversion is complex because of Unicode alignment, null termination, explicit byte lengths, and legacy ASCII4 prefixes. `req_data_oob()` is the central defense against pointer/count wraparound. Handle lookup must preserve session isolation even though SMB permits mixed sessions and tree IDs. `smbsrv_send_reply_nosign()` is necessary for special packets but should not leak into normal signed responses.

## Test Signals
Cover Unicode and ASCII string parsing, malformed unterminated strings, ASCII4 empty behavior, blob bounds and wraparound checks, chained reply buffer growth, negotiated max transmit enforcement, NTSTATUS-to-DOS conversion, no-sign negotiation/raw responses, file handle creation/make-valid/destroy/search-by-wire-key, and cross-session FID rejection.
