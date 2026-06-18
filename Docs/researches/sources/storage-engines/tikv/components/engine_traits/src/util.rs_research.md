# sources/storage-engines/tikv/components/engine_traits/src/util.rs

Purpose: Supplies key-range validation and sequence-number window utilities for write ordering and memtable flush coordination.

Important APIs and control flow: `check_key_in_range` returns `NotInRange` unless a key is within `[start,end)`, treating empty end as unbounded. Global atomics allocate write counters, memtable versions, and max synced sequence number access. `SequenceNumber::pre_write` reserves a contiguous write counter, `post_write` attaches backend sequence number and end counter, and `max` compares by sequence number. `SequenceNumberWindow::push` receives sequence numbers out of order, tracks contiguous received start counters, uses pending end-counter mapping, advances committed sequence number when all prior writes are received, and exposes committed seqno and pending count.

State, persistence, and dependencies: State is process-global atomics plus in-memory window queues/maps; committed sequence numbers represent persistence/order coordination but are not directly durable here.

Integration points, risks, and test signals: Used by asynchronous write/flush paths that need contiguous commit tracking. Risks include global counter wrap, duplicate/old sequence handling, assumptions about end-counter monotonicity, unbounded pending windows under lost notifications, and panic assertions. Tests cover out-of-order sequence receipt and benchmark high-volume window updates.
