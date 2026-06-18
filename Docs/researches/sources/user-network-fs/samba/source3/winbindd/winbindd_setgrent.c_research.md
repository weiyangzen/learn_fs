<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c

## Purpose
This file implements the asynchronous `WINBINDD_SETGRENT` command, which resets per-client group enumeration state before `GETGRENT` calls.

## Important APIs, Types, And Functions
The public entry points are `winbindd_setgrent_send()` and `winbindd_setgrent_recv()`. The state struct is only a dummy tevent state because the command completes immediately after setting `cli->grent_state`.

## Control Flow
`send()` creates a tevent request, frees any previous `cli->grent_state`, logs the client and `winbind enum groups` setting, and either completes immediately when group enumeration is disabled or allocates a fresh `struct getgrent_state` under the client. It posts the completed request to the event loop. `recv()` logs command completion and returns OK.

## State And Persistence Behavior
The only state mutation is per-client in-memory `cli->grent_state`. No persistent storage is touched. Disabling enumeration leaves the state cleared, causing later enumeration to produce no entries.

## Dependencies And Integration Points
It depends on tevent, talloc, `winbindd_cli_state`, `getgrent_state`, and the `lp_winbind_enum_groups()` configuration. It is used by traditional NSS clients and by varlink group/membership enumeration code that synthesizes internal winbind requests.

## Risks And Test Signals
Risks are low but include stale enumeration state if callers skip `ENDGRENT`, and behavior changes when `winbind enum groups` is disabled. Test signals are set/get/end group enumeration sequences and varlink enumeration behavior with enumeration enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c -->
