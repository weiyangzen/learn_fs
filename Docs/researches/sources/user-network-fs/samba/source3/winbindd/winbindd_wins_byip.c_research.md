<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c

## Purpose
This file implements the asynchronous `WINBINDD_WINS_BYIP` command. It performs a NetBIOS node status query for a numeric IP address and returns matching workstation/server names.

## Important APIs, Types, And Functions
The entry points are `winbindd_wins_byip_send()`, `winbindd_wins_byip_done()`, and `winbindd_wins_byip_recv()`. State includes the wildcard NetBIOS name, parsed socket address, and fixed-size response buffer.

## Control Flow
`send()` null-terminates the client request string, initializes the response as `<ip>\t`, creates a wildcard `*` NetBIOS name, parses the IP with `interpret_string_addr(..., AI_NUMERICHOST)`, and dispatches `node_status_query_send()`. The callback receives node status names, filters out group names and non-0x20 entries, appends names separated by spaces, replaces the trailing space/tab with newline, and completes the request.

## State And Persistence Behavior
All state is request-local. The command sends network queries but does not persist data.

## Dependencies And Integration Points
It depends on Samba namequery/nmblib helpers, tevent, fixed `fstring` response handling, and winbind request/response structures. It serves legacy WINS lookup clients.

## Risks And Test Signals
Risks include response buffer overflow, invalid numeric address handling, no matching 0x20 names causing the tab to become a newline, and IPv4/IPv6 formatting compatibility. Tests should cover invalid input, single and multiple names, group-name filtering, and oversized response handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c -->
