# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_validator.rs

Purpose: this file provides a small concurrent cache for temporarily disabling split decisions for specific regions. It is used by load-based split control to avoid repeatedly splitting regions that should be suppressed for a bounded time.

Important APIs and types:
- `SplitValidatorCore<P>` stores disabled region ids in a `crossbeam_skiplist::SkipMap<u64, Instant>`, plus capacity, GC offset, and a pluggable GC predicate.
- `SplitValidator` wraps `Arc<SplitValidatorCore<fn(...) -> bool>>` and exposes `new`, `is_disabled`, `disable`, and `enable`.
- Constants define capacity (`0x8000`), max entries scanned per GC (`0x80`), and TTL (`600s`).

Control flow:
- `disable(region_id)` inserts the current instant and then calls incremental `gc`.
- `is_disabled(region_id)` checks the skiplist; if the GC predicate says the entry is expired, it removes the entry and returns false.
- `enable(region_id)` removes the entry directly.
- `gc` tries to acquire a mutex-protected offset. If capacity is not reached and no GC round is in progress, it exits. Otherwise it scans at most `GC_ENTRY_LIMIT` entries from the offset, removes expired entries, and resets the offset when the scan reaches the end.

State and persistence behavior:
- State is entirely in-memory and shared by clone through `Arc`.
- Expiration is based on wall-clock `Instant::elapsed`; restart clears disabled state.
- The skiplist supports concurrent reads/writes, while the offset mutex bounds GC work and avoids multiple concurrent incremental scans.

Dependencies and integration points:
- Depends on `crossbeam_skiplist` for concurrent map behavior.
- Used by `AutoSplitController::flush` to skip regions marked disabled.
- Constructed and passed through PD worker code along with the auto split controller.

Risks and edge cases:
- GC only runs on `disable` and opportunistically on `is_disabled` for that key; a quiet cache can retain expired entries until later activity.
- `gc_offset` advances by `key + 1`; region id `u64::MAX` would wrap if present, although region ids are expected to stay below that.
- The TTL is fixed in this file and not online-configurable.

Test signals:
- Tests cover multi-region disable/enable, enabling absent regions, expiration via injected predicate, incremental GC offset movement and removal behavior, disable-triggered GC at capacity, and a mixed-operation benchmark over many region ids.
