# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_fsav.c

## Purpose
This file implements the F-Secure Anti-Virus `fsavd` backend for `vfs_virusfilter`. It configures fsavd protocol options, scans files through the daemon socket, and translates tab-delimited scanner events into virusfilter results.

## Important APIs, Types, and Functions
`struct virusfilter_fsav_config` stores backend options: protocol version, riskware scanning, stop-on-first behavior, and filename filtering. `virusfilter_fsav_connect()` reads backend-specific smb.conf values and sets `config->block_suspected_file`. `virusfilter_fsav_scan_init()` reuses or opens the Unix socket, validates the `DBVERSION` greeting, and sends `PROTOCOL` plus multiple `CONFIGURE` commands. `virusfilter_fsav_scan()` sends `SCAN\t<cwd>/<fname>`, reads replies until `OK`, and maps `CLEAN`, infection/riskware tokens, suspected tokens, `SCAN_FAILURE`, and unknown replies. `virusfilter_fsav_scan_end()` disconnects.

## Control Flow
On VFS connect, the backend config object is allocated under `config->backend` and given a destructor that closes the scanner connection. Each scan initializes the protocol if needed, sends the scan command, loops over scanner events, updates the result/report as significant records arrive, then returns when an `OK` terminator is read or an I/O/protocol error occurs.

## State and Persistence
Backend state is in `backend_private`. The socket stream can persist between scans and is health-checked with a best-effort `PING`. It defaults to `/tmp/.fsav-0` unless overridden. No data is persisted by the backend itself.

## Dependencies and Integration Points
It depends on the shared virusfilter I/O line protocol helpers and F-Secure fsavd's tab-delimited local socket protocol. It integrates suspected-file policy through the core `block_suspected_file` field.

## Risks
The comments note uncertainty around the correct `PING` command; false connection reuse or false reconnects are possible. Reply parsing assumes `strtok_r()` returns non-null tokens before `strcmp()`, so malformed empty replies are risky. Riskware is mapped to infected when emitted by fsavd, which is policy-sensitive.

## Test Signals
Mock fsavd sessions should cover greeting/configure success and failure, connection reuse, clean/infected/riskware/suspected/scan-failure tokens, malformed empty lines, and `block suspected file` true versus false.
