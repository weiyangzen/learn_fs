# sources/storage-engines/wiredtiger/src/include/tiered.h

Purpose: `tiered.h` declares the in-memory model for WiredTiger tiered storage: local and shared tier slots, per-tier operation capabilities, background work units, tiered table handles, and object/tree descriptors.

Important APIs and types: constants define tier indexes (`WT_TIERED_INDEX_LOCAL`, `WT_TIERED_INDEX_SHARED`, `WT_TIERED_INDEX_INVALID`), `WT_TIERED_MAX_TIERS`, object-name flags, `WT_FLUSH_STATE_DONE`, work-unit types (`WT_TIERED_WORK_FLUSH`, `WT_TIERED_WORK_FLUSH_FINISH`, `WT_TIERED_WORK_REMOVE_LOCAL`, `WT_TIERED_WORK_REMOVE_SHARED`), work flags, `WT_TIERED_WORK_UNIT`, `WT_TIERED_TIERS`, `WT_TIERED`, `WT_TIERED_OBJECT`, and `WT_TIERED_TREE`.

Control flow: tiered tables maintain a local writable tier and a shared tier that can receive flushed objects. Flush and cleanup paths enqueue `WT_TIERED_WORK_UNIT` records with an operation type, object id, tiered handle, and force/free flags. Worker code dequeues units, performs object flush/finish/remove operations, and uses the tier definitions to decide whether a tier supports read, write, or flush.

State and persistence behavior: the structures mirror metadata that describes tiered tables and object ids, but the header itself stores only in-memory handles. `current_id`, `next_id`, and `oldest_id` track object generations for a tiered handle; object descriptors include URI, approximate count, size, switch transaction/timestamp, id, generation, reference count, and local-residency flag. Actual persistence occurs through metadata and bucket storage implementations.

Dependencies and integration points: the header depends on `WT_DATA_HANDLE`, `WT_BUCKET_STORAGE`, `TAILQ_ENTRY`, timestamps, and atomic helpers. It integrates with metadata creation/open, tiered cursor/open logic, background flush-tier workers, object naming helpers, and statistics such as `flush_tier`, `local_objects_inuse`, and tiered work-unit counters from `stat.h`.

Risks: several object/tree structures are marked currently unused, so future code can accidentally assume invariants that are not maintained. Object id transitions and flush-state atomic counters must stay synchronized with metadata publication or readers may miss shared objects or retain local objects too long. Static tier slots simplify initial design but require care if more than local/shared tiers become active.

Test signals: tiered table create/open/reopen tests, `flush_tier` success and skip cases, forced flush behavior, local-object removal, shared-object removal, object naming with each flag combination, metadata crash/recovery around object id changes, and background work queue tests that verify unit counters and free semantics.
