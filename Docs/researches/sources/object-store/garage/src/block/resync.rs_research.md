# sources/object-store/garage/src/block/resync.rs

Purpose: manages the asynchronous queue that reconciles local block files with local reference counts and cluster placement expectations.

Important APIs/types/functions: `BlockResyncManager`, persistent `ResyncPersistedConfig`, queue constants, `put_to_resync`, `put_to_resync_at`, `clear_backoff`, `clear_resync_queue`, `register_bg_vars`, `resync_iter`, `resync_block`, `ResyncWorker`, `ErrorCounter`, and `BusyBlock`.

Control flow: resync queue keys are timestamp plus hash, ordered by due time. Workers claim non-busy queue entries, honor due time and exponential backoff in `errors`, run `resync_block`, then clear or update error/backoff state. `resync_block` deletes locally unneeded blocks after optional offload to nodes that need them, clears deletable RC entries, or fetches missing needed blocks from remote storage nodes if the current layout says this node should store them.

State and persistence: persistent DB trees `block_local_resync_queue` and `block_local_resync_errors`; `resync_cfg` persists worker count and tranquility. Error counters encode two u64 values: consecutive errors and last try time. In-memory busy set prevents duplicate concurrent processing of the same queue key.

Dependencies and integration points: uses `garage_db`, `garage_util` background/persister/time/metrics/tranquilizer, `garage_rpc`, OpenTelemetry, and `BlockManager` read/write/delete/RPC methods. Exposed to admin block commands for listing errors and retrying backoff.

Risks: correctness depends on tolerating inconsistent queue/error state and ordering insert-before-remove to survive crashes. Missing needed block fetch can fail repeatedly until backoff; recalculating RC on missing remote data may repair metadata but also surfaces data-loss scenarios. Offload refuses when write quorum is unavailable, delaying deletion. The comment says no more than four workers, but the constant is eight, so operational expectations should follow the constant/API.

Test signals: no local tests; integration should verify backoff encoding, clear-backoff, queue persistence across restart, missing-block fetch, unneeded-block offload/delete, and multi-worker busy-set behavior.
