# sources/user-network-fs/samba/source3/nmbd/nmbd_incomingdgrams.c

## Purpose
Handles browser-service datagram payloads received on the NetBIOS datagram path, mostly mailslot `\\MAILSLOT\\BROWSE` announcements and requests. It updates browse databases, detects local-master conflicts, queues DMB synchronization, answers backup-list requests, processes browser resets, and reacts to LanMan traffic.

## Important APIs, Types, And Functions
Public handlers include `process_host_announce()`, `process_workgroup_announce()`, `process_local_master_announce()`, `process_master_browser_announce()`, `process_lm_host_announce()`, `process_get_backup_list_request()`, `process_reset_browser()`, `process_announce_request()`, and `process_lm_announce_request()`. Internal `send_backup_list_response()` builds `ANN_GetBackupListResp`.

## Control Flow
Host, workgroup, local-master, and LanMan announcements parse TTL/type/name/comment fields and create, update, or remove workgroup/server records. Local-master announcements targeting a workgroup where Samba already thinks it is LMB trigger a browser reset to the peer, demotion, and a new election. Master-browser announcements are accepted only when Samba is configured and currently acting as DMB, then they create/refresh `lmb_browserlist` entries. Backup-list requests are answered only for Samba's workgroup and only when addressed to `<1b>` while DMB or `<1d>` while LMB. Reset packets can force demotion and/or expire browse lists.

## State And Persistence
Mutates workgroup/server lists, TTLs, comments, local master names, `subrec->work_changed`, global `found_lm_clients`, the LMB browser cache, and role state through demotion calls. Persistence is indirect through browse database writers and name-release paths.

## Dependencies, Risks, And Test Signals
Depends on server/workgroup database helpers, election/LMB APIs, mailslot sending, browser cache, and configuration. Risks include accepting malformed legacy announcements, unnecessary demotion churn, and LanMan buffer parsing assumptions. Test signals include browse database changes after announcements, demotion on duplicate LMB, DMB cache creation, backup-list responses, reset expiry, and `found_lm_clients` toggling.
