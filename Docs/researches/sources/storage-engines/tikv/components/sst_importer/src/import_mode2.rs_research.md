# sources/storage-engines/tikv/components/sst_importer/src/import_mode2.rs

Purpose: tracks import mode at key-range granularity for V2 import flows rather than mutating global RocksDB options.

Important APIs and types: `HashRange` is a hashable start/end key range converted from protobuf `Range`. `ImportModeSwitcherV2` wraps a mutex containing timeout and `HashMap<HashRange, Instant>`. Public methods add ranges, clear ranges, check whether a region or range overlaps active import ranges, list active ranges, and start timeout cleanup.

Control flow: `ranges_enter_import_mode` inserts or refreshes ranges with `now + timeout`. `start_resizable_threads` runs a background timer that clears previously selected expired ranges, then finds the minimum next expiration and waits until then. `region_in_import_mode` and `range_in_import_mode` scan active ranges and use half-open overlap checks where empty end key means unbounded.

State and persistence behavior: in-memory map only. Import-mode membership disappears on process restart or switcher drop.

Dependencies and integration points: used by SST importer V2 range import tracking and exported helper `range_overlaps` from crate root. Depends on import protobuf `Range`, metapb `Region`, global timer, and resizable runtime handle.

Risks: overlap checks are byte-lexicographic and assume encoded key ordering. The timer loop only clears ranges that were identified in the previous iteration as earliest expirations, then recomputes; correctness depends on renewed ranges updating their expiration before cleanup. Scanning all ranges for every region/range check can be costly with many active ranges.

Test signals: tests cover region/range overlap edge cases, adding/clearing ranges and region membership, and timeout behavior with renewed ranges.
