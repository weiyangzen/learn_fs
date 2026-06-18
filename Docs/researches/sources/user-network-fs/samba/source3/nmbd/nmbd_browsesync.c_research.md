# sources/user-network-fs/samba/source3/nmbd/nmbd_browsesync.c

## Purpose
Coordinates browser-list synchronization between local master browsers and domain master browsers. It covers DMB syncing from cached LMBs, LMB discovery/sync with its DMB through WINS, and DMB discovery/sync with other DMB workgroups registered in WINS.

## Important APIs, Types, And Functions
Public functions are `dmb_expire_and_sync_browser_lists()`, `announce_and_sync_with_domain_master_browser()`, `collect_all_workgroup_names_from_wins_server()`, and `sync_all_dmbs()`. Internal helpers include `sync_with_lmb()`, `announce_local_master_browser_to_domain_master_browser()`, `sync_with_dmb()`, node-status success/fail callbacks, and WINS query success/fail callbacks.

## Control Flow
As a DMB, `dmb_expire_and_sync_browser_lists()` runs at most every 20 seconds, expires stale `lmb_browserlist` entries, and syncs entries whose `sync_time` passed. As an LMB, `announce_and_sync_with_domain_master_browser()` requires WINS client mode, queries `WORKGROUP<1b>`, caches or resolves the DMB `<20>` name by node status, sends `ANN_MasterAnnouncement`, and calls `sync_browse_lists()`. `collect_all_workgroup_names_from_wins_server()` queries `*<1b>` at most every 15 minutes and node-statuses each returned DMB IP. `sync_all_dmbs()` randomly syncs with known foreign workgroups at most every 5 minutes to control traffic.

## State And Persistence
Mutates `browse_cache_record::sync_time`, `work->dmb_name`, `work->dmb_addr`, `work->local_master_browser_name`, and the unicast workgroup list. It creates transient `userdata_struct` values for async callbacks. Persistence is indirect through workgroup/server database writers.

## Dependencies, Risks, And Test Signals
Depends on browser cache, WINS name queries, node-status requests, mailslot datagrams, and `sync_browse_lists()`. Risks include stale cached DMB names, fragile node-status parsing heuristics, and throttling failures causing expensive discovery. Test signals include master-announcement packets, `<20>`/`<1b>` extraction from node-status replies, sync invocations with correct flags, and timer throttling.
