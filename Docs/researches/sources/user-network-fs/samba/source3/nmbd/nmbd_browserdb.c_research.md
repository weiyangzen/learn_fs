# sources/user-network-fs/samba/source3/nmbd/nmbd_browserdb.c

## Purpose
Maintains the in-memory cache of local master browsers known to this nmbd when acting as a domain master browser. The cache drives later DMB-to-LMB browse-list synchronization and expires LMB entries that stop announcing themselves.

## Important APIs, Types, And Functions
The file owns global `struct browse_cache_record *lmb_browserlist`. Public functions are `create_browser_in_lmb_cache()`, `find_browser_in_lmb_cache()`, `update_browser_death_time()`, and `expire_lmb_browsers()`. Records store uppercased LMB name, workgroup, IP address, next `sync_time`, and `death_time`.

## Control Flow
`create_browser_in_lmb_cache()` allocates a record, schedules first sync one minute in the future, sets death time to `CHECK_TIME_MST_ANNOUNCE + 2` minutes, uppercases names, stores the IP, and appends the entry. `find_browser_in_lmb_cache()` performs linear lookup by browser name. `update_browser_death_time()` extends liveness on fresh announcements. `expire_lmb_browsers(t)` removes stale entries.

## State And Persistence
All state is process-local memory. The cache is derived from incoming master-browser announcements and is lost on restart.

## Dependencies, Risks, And Test Signals
`nmbd_incomingdgrams.c` creates/refreshes entries; `nmbd_browsesync.c` expires and syncs them. The cache is keyed only by browser name, so same-named LMBs across workgroups/scopes can collide. Test signals include entry creation, death-time refresh, expiry, and later `sync_browse_lists()` attempts.
