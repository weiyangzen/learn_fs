# sources/user-network-fs/samba/source3/utils/net_time.c

## Purpose
Implements `net time` for querying a remote SMB server's time, formatting it for display or `/bin/date`, showing the remote timezone offset, or setting the local system clock.

## Important APIs, Types, and Functions
`cli_servertime()` connects with `cli_connect_nb()`, negotiates using `smbXcli_negprot()`, reads `cli_state_server_time()`, and optionally retrieves `smb1cli_conn_server_time_zone()`. `systime()` formats time as `MMDDhhmmYYYY.ss`. Subcommands are `system`, `set`, and `zone`.

## Control Flow
No-arg `net_time()` locates a target from host/IP or `find_master_ip()` and prints `ctime()`. `system` prints `systime()`. `set` calls `settimeofday()` with remote time. `zone` converts the SMB timezone value into signed HHMM.

## State and Persistence
Read paths are transient network operations. `set` mutates local system time. Target discovery may set `c->opt_have_ip` and `c->opt_dest_ip`.

## Dependencies and Integration Points
Depends on libsmb client connection, NetBIOS name lookup, SMB transport/protocol loadparm settings, and common net usage/dispatch.

## Risks
Setting system time can disrupt authentication and services. A returned time of `0` is treated as failure. NetBIOS-disabled environments and negotiation failures are common operational cases.

## Test Signals
Cover host/IP and discovered targets, connection/negotiation failure, `system` formatting, `zone` conversion, `settimeofday()` failure, NetBIOS-disabled message, and usage for missing host in subcommands.
