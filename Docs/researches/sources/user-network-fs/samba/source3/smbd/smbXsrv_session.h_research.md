# sources/user-network-fs/samba/source3/smbd/smbXsrv_session.h

## Purpose
Public interface for smbd session management. It hides the internal table/global-record implementation while exposing session creation, authentication tracking, lookup, shutdown, logoff, traversal, previous-session closure, and lease-break wait helpers.

## Important APIs, Types, and Functions
Forward-declares `messaging_context`, `smbXsrv_client`, `smbXsrv_connection`, `smbXsrv_session`, `smbXsrv_session_global0`, `smbXsrv_channel_global0`, and `smbXsrv_session_auth0`. Exports `smbXsrv_session_global_init()`, `smbXsrv_session_create()`, `smbXsrv_session_add_channel()`, `smbXsrv_session_remove_channel()`, lookup helpers for SMB1/SMB2/global/local contexts, `smbXsrv_session_info_lookup()`, `get_valid_smbXsrv_session()`, traversal callbacks, async shutdown, async close-previous, and `smbXsrv_wait_for_handle_lease_break()`.

## Control Flow
Callers initialize protocol-specific tables after negotiation, create sessions during session setup, create pending auth records for in-progress authentication, update global records once keys/auth state change, and use lookup wrappers to validate incoming request session IDs. Logoff and disconnect paths call the exported shutdown/logoff/remove-channel routines. Internal consumers can traverse local or global session records through callback-based APIs.

## State and Persistence
The header itself owns no state, but its API boundary distinguishes local live process state from global persisted state. `smbXsrv_session_info_lookup()` intentionally exposes authenticated session info to consumers such as UID switching, while `get_valid_smbXsrv_session()` is documented as an internal post-validation helper rather than a request validator.

## Dependencies and Integration Points
Includes `replace.h`, `tevent.h`, NTSTATUS utilities, and time types. Its types are completed by smbd global/session structures and generated NDR headers in implementation files. It is included by UID handling, request processing, SMB2 session setup/logoff, connection teardown, and service enumeration code.

## Risks
The API has similarly named lookup helpers with different validation strength. Using `get_valid_smbXsrv_session()` for wire request validation would bypass channel/status checks. Async APIs require callers to follow tevent ownership and recv conventions. Functions returning borrowed session/auth info depend on live session object lifetime.

## Test Signals
Compile-time coverage should catch signature drift across smbd callers. Runtime coverage should validate that SMB1, SMB2 connection-local, client-local, and global lookups return distinct expected statuses for deleted, unauthenticated, expired, and wrong-channel sessions.
