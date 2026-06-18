# sources/user-network-fs/samba/source4/smb_server/smb2/find.c

## Purpose
This file implements SMB2 QUERY_DIRECTORY handling. It translates SMB2 find levels and request fields into the legacy raw search-first/search-next NTVFS interfaces, accumulates directory entries into a passthrough SMB2 blob, and serializes the find reply.

## Important APIs, Types, And Functions
The public entry point is `smb2srv_find_recv`. Internal support centers on `struct smb2srv_find_state`, `smb2srv_find_backend`, `smb2srv_find_callback`, and `smb2srv_find_send`. The state object tracks the original request, current `struct smb2_find`, optional `union smb_search_first` or `union smb_search_next`, and the last entry offset that must have its next-entry link cleared before the reply is sent.

## Control Flow
`smb2srv_find_recv` validates a dynamic 0x20 request, allocates both a `struct smb2_find` and a wrapper state, decodes find level, flags, file index, directory handle, pattern, and max response size, normalizes NULL patterns to the empty string, validates the handle, and dispatches. `smb2srv_find_backend` maps SMB2 find information classes to raw search data levels, then chooses `ntvfs_search_first` when `SMB2_CONTINUE_FLAG_REOPEN` is present, otherwise `ntvfs_search_next`. The callback appends entries using `smbsrv_push_passthru_search`; if the blob would exceed the max response, it rolls back and stops enumeration.

## State And Persistence
State is per request only. Directory enumeration cursor semantics are owned by the NTVFS backend and the handle. The reply blob is grown under the request state and trimmed by resetting the final next-entry offset to zero. No durable storage is directly changed.

## Dependencies And Integration Points
The file depends on SMB2 helpers, raw search unions, `smbsrv_push_passthru_search`, and NTVFS search calls. It is dispatched by `receive.c` for `SMB2_OP_QUERY_DIRECTORY` after session, tcon, and handle validation support from other modules.

## Risks And Test Signals
Risks include incomplete information-class mapping, returning `NT_STATUS_FOOBAR` for unknown levels, off-by-one response sizing, last-entry offset corruption, and empty pattern behavior. Useful tests cover every SMB2 find class, small `max_response_size`, reopen vs next modes, wildcard and empty patterns, invalid handles, and backend callbacks that stop mid-enumeration.
