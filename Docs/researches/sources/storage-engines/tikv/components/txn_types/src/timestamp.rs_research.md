# sources/storage-engines/tikv/components/txn_types/src/timestamp.rs

Purpose: timestamp wrapper and small immutable timestamp-set abstraction for transaction code.

Important APIs/types/functions: `TimeStamp`, `TSO_PHYSICAL_SHIFT_BITS`, `compose`, `physical`, `logical`, `next`, `prev`, `incr`, `decr`, `physical_now`, and `TsSet`.

Control flow: `TimeStamp` is a transparent `u64` wrapper whose high bits encode physical milliseconds and low 18 bits encode logical counter. `TsSet::new` chooses empty, small `Arc<[TimeStamp]>`, or `Arc<HashSet<TimeStamp>>` representation based on size; `contains` dispatches to the chosen representation.

State and persistence: timestamps are value types persisted throughout MVCC/lock/write metadata. `TsSet` is immutable shared in memory through `Arc`.

Dependencies/integration: used by lock conflict bypass sets, key timestamp parsing tests, transaction metadata, and heap-size accounting.

Risks: `next/prev/incr/decr` assert at bounds; unsafe vector transmute from `Vec<u64>` depends on transparent representation; `physical_now` unwraps system time since Unix epoch.

Test signals: tests cover physical/logical splitting, key timestamp split integration, and all `TsSet` representations/contains behavior.
