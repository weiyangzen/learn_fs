# sources/storage-engines/wiredtiger/test/format/follower.c

## Purpose
`follower.c` implements disaggregated-storage follower checkpoint pickup. It polls the configured page log, fetches checkpoint metadata, enforces timestamp safety, and reconfigures a follower connection to a newer checkpoint.

## Important APIs, Types, And Functions
Important functions are `follower_fetch_full_metadata`, `follower_try_pickup_checkpoint`, `follower_read_latest_checkpoint`, and exported worker `WT_THREAD_RET follower(void *)`. It uses `WT_PAGE_LOG`, `WT_PAGE_LOG_HANDLE`, `WT_PAGE_LOG_GET_COMPLETE_CHECKPOINT_ARGS`, `WT_DISAGG_METADATA`, `__wt_disagg_parse_meta`, `timestamp_query`, `conn->reconfigure`, and `conn->get_page_log`.

## Control Flow
The worker opens a session and page-log handle, then loops until `g.workers_finished`. Each cycle clears prior checkpoint metadata, calls `pl_get_complete_checkpoint`, tolerates `WT_NOTFOUND`, and if metadata changed from `g.checkpoint_metadata`, tries to pick it up. Pickup fetches full metadata by reading the metadata page at `metadata_lsn`, parses `oldest_timestamp`, compares it with the follower pinned timestamp, and only reconfigures when safe. The loop sleeps 1-3 seconds between polls.

## State And Persistence Behavior
The follower stores the last accepted checkpoint metadata string in `g.checkpoint_metadata` and changes the WiredTiger connection's disaggregated checkpoint state with `conn->reconfigure`. It allocates/free checkpoint metadata buffers and full metadata buffers but writes no format files.

## Dependencies And Integration Points
It depends on disaggregated page-log configuration, transaction timestamps, pinned timestamp queries, PALI metadata IDs, and global leader/follower state. `format_disagg.c` calls `follower_read_latest_checkpoint` during role switch from leader to follower.

## Risks And Test Signals
Risks include picking a checkpoint whose oldest timestamp is newer than pinned, stale metadata comparison with fixed-size `g.checkpoint_metadata`, page-log implementations without complete-checkpoint support, and memory ownership mistakes around `WT_ITEM.mem`. Signals include follower pickup/skip messages, `WT_NOTFOUND` polling, and validation failures after role switching or multi-node comparison.
