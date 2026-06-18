# sources/user-network-fs/samba/source3/nmbd/nmbd_sendannounce.c

## Purpose
`nmbd_sendannounce.c` builds and sends NetBIOS datagram announcements for SMB browser service discovery, including local server announcements, local master/browser workgroup announcements, LanMan compatibility announcements, remote announces, remote browse sync, and shutdown removal notices.

## Important APIs, types, and functions
- `send_browser_reset` and `broadcast_announce_request` send browser control datagrams.
- `announce_my_server_names` and `announce_my_lm_server_names` emit periodic host announcements.
- `announce_myself_to_domain_master_browser`, `announce_my_servers_removed`, `announce_remote`, and `browse_sync_remote` implement domain-master, shutdown, and remote configured paths.
- Internal builders `send_announcement` and `send_lm_announcement` encode fixed-format payloads.

## Control flow
Timer-driven functions inspect subnets, workgroups, and server records, decide whether intervals have elapsed, build browser payloads, and send them through `send_mailslot`. Normal announcements ramp interval length and honor `needannounce`. Remote paths parse configured target tokens and send announcements for all local NetBIOS names.

## State and persistence behavior
The file mutates in-memory timing state on `work_record` objects plus static announce timers. It consumes `updatecount` from the server-list database. Persistent browse-list output is handled by `nmbd_serverlistdb.c`.

## Dependencies and integration points
Dependencies include `send_mailslot`, subnet/workgroup/server-list state, local NetBIOS name enumeration, loadparm remote/LM settings, browser-sync APIs, service type constants, and Samba string helpers.

## Risks and edge cases
Fixed-format browser datagrams are sensitive to length and interval-unit mistakes. `FIRST_SUBNET` source selection may be surprising on multi-interface hosts. LanMan auto mode depends on detecting LM clients. Shutdown removal only announces current local server records.

## Test signals
Tests should inspect mailslot payloads for host, local-master, workgroup, LM, remote, reset, and removal paths, and verify timer gating and `needannounce` behavior.
