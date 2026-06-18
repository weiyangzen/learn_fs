# sources/user-network-fs/samba/source3/winbindd/winbindd_endgrent.c

## Purpose
Implements async `WINBINDD_ENDGRENT`, the end-of-enumeration command for group database iteration. It releases per-client group enumeration state held on the winbind client object.

## Important APIs, Types, And Control Flow
`winbindd_endgrent_send()` creates a trivial tevent request, logs the client command, frees `cli->grent_state` with `TALLOC_FREE()`, marks the request done, and posts it. `winbindd_endgrent_recv()` only logs completion and returns `NT_STATUS_OK`.

## State And Persistence
The only state change is freeing `winbindd_cli_state.grent_state`. This can affect any outstanding `GETGRENT` request using the same client state; `winbindd_getgrent.c` explicitly detects that race and reports `NT_STATUS_INVALID_PARAMETER`.

## Dependencies And Integration Points
Depends on `winbindd.h`, tevent request conventions, and the enumeration state allocated by setgrent/getgrent code elsewhere.

## Risks And Test Signals
The handler always returns success after request creation, even if no enumeration was active. Test normal `setgrent/getgrent/endgrent`, repeated `endgrent`, `endgrent` before enumeration, and an interleaved end while a batch `GETGRENT` is outstanding.
