# sources/user-network-fs/libsmb2/lib/smb2-cmd-session-setup.c

## Purpose
Encodes and decodes SMB2 SESSION_SETUP requests and replies, carrying authentication security buffers and updating the active session id.

## Important APIs, Types, And Functions
Exports `smb2_cmd_session_setup_async`, `smb2_cmd_session_setup_reply_async`, `smb2_process_session_setup_fixed`, `smb2_process_session_setup_variable`, `smb2_process_session_setup_request_fixed`, and `smb2_process_session_setup_request_variable`. It works with `struct smb2_session_setup_request` and `struct smb2_session_setup_reply`.

## Control Flow
Request encoding emits flags, security mode, capabilities, channel, fixed security buffer offset, length, previous session id, and then appends the caller-provided security blob. Reply encoding writes session flags and appends a padded security response buffer. Client reply parsing validates fixed structure, checks security-buffer end against the SPL, updates `smb2->session_id` from the SMB2 header, and returns the variable buffer length. Server request parsing reads request fields and returns the security buffer length for subsequent variable parsing.

## State And Persistence
The most important state transition is storing `smb2->session_id = smb2->hdr.session_id` on a parsed reply. Security buffers point into iovec memory, not independently copied, so their lifetime follows the PDU/input vector. Previous session id is carried for reconnect/session binding semantics.

## Dependencies And Integration Points
This file sits between authentication code and the generic PDU/socket layer. It influences signing behavior because signing starts only after a valid session and session key exist. It also participates in server-mode request parsing for authentication negotiation.

## Risks
The server request parser has the security-buffer offset read commented out and returns only the length, implicitly assuming the variable bytes immediately follow the fixed payload. It also reads `previous_session_id` at offset 18, while encoding writes it at offset 16, which is suspicious and needs protocol test coverage. Security buffer allocation with zero length is not specially handled in request encoding.

## Test Signals
Cover empty and non-empty security buffers, multi-leg auth, previous-session reconnect, malformed offsets and lengths, session id propagation, server-mode request parsing, and signing behavior immediately before and after session setup completion.
