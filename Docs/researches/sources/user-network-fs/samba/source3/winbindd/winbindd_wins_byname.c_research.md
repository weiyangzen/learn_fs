<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c

## Purpose
This file implements the asynchronous `WINBINDD_WINS_BYNAME` command. It resolves a NetBIOS name to IP addresses through WINS first and broadcast fallback second.

## Important APIs, Types, And Functions
The command uses `winbindd_wins_byname_send()`, `winbindd_wins_byname_wins_done()`, `winbindd_wins_byname_bcast_done()`, and `winbindd_wins_byname_recv()`. State tracks the event context, original request, returned socket-address array, and count.

## Control Flow
`send()` null-terminates the name and calls `resolve_wins_send()` for type 0x20. If WINS succeeds, the request completes. If it fails, the callback starts `name_resolve_bcast_send()`. `recv()` formats returned addresses separated by spaces followed by a tab, original name, and newline, then copies the result into the fixed winbind response buffer after checking size.

## State And Persistence Behavior
State is request-local and network-derived. No persistent storage is updated.

## Dependencies And Integration Points
It depends on namequery, nmblib, socket address formatting, tevent, and winbind response structures. It integrates with legacy WINS-by-name winbind clients.

## Risks And Test Signals
Risks are fallback timing, address-list formatting, response marshalling overflow, and behavior when WINS fails but broadcast succeeds. Tests should cover WINS success, broadcast fallback, total failure, multiple addresses, and oversized responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c -->
