# sources/user-network-fs/samba/source4/nbt_server/dgram/netlogon.c

## Purpose

`dgram/netlogon.c` handles Netlogon mailslot datagrams for DC discovery. It answers legacy GETDC and ADS-style SAM_LOGON requests when the NBT server is listening on the requested NetBIOS name and the local server role/domain conditions are satisfied.

## Important APIs, Types, and Functions

Main helpers are `nbtd_netlogon_getdc()`, `nbtd_netlogon_samlogon()`, `nbtd_mailslot_netlogon_reply()`, and exported callback `nbtd_mailslot_netlogon_handler()`. It uses `fill_netlogon_samlogon_response()`, `samdb_is_pdc()`, `nbtd_find_iname()`, `nbtd_find_reply_iface()`, `dgram_mailslot_netlogon_parse_request()`, and `dgram_mailslot_netlogon_reply()`.

## Control Flow

Incoming mailslot packets are checked against local registered names, parsed as Netlogon requests, and dispatched by command. `LOGON_PRIMARY_QUERY` is answered only for PDC/LOGON destination names, only when Samba is an AD DC and PDC for the local workgroup. `LOGON_SAM_LOGON_REQUEST` builds a richer SAM_LOGON response using the SAM database, optional domain SID, requested username/account control, source address, and requested Netlogon version. Successful responses are sent from the best reply interface to the caller's requested mailslot.

## State and Persistence Behavior

The file reads `nbtsrv->sam_ctx`, loadparm role/workgroup/netbios name, and interface registration state. It does not persist data; replies are transient allocations under the mailslot handler context.

## Dependencies and Integration Points

Dependencies include libdgram Netlogon parse/reply helpers, DSDB/SAMDB, auth/security helpers, loadparm, server role helpers, and NBT interface selection. It is registered for both NETLOGON and NTLOGON mailslot names in `dgram/request.c`.

## Risks and Test Signals

Risks include responding to the wrong domain/name, mismatched PDC role detection, SAMDB response construction failures, reply-interface selection problems, and broad handling of NTLOGON through the Netlogon parser. Tests should cover PDC and non-PDC roles, wrong domain names, unknown commands, malformed packets, SID and no-SID SAM_LOGON, and reply source address correctness.
