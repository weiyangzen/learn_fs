# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor15.py

Purpose: exhaustive-ish follower layered cursor iteration over combinations of key states. It models each key as ingest only (`I`), stable only (`S`), both (`B`), stable hidden by ingest tombstone (`R`), or ingest tombstone with no stable row (`X`), then verifies iteration and point lookup for many generated state strings.

Important APIs and functions: top-level `generate_unique_situations(max_len)` builds state sequences with bounded repetition. `test_layered_cursor15` uses `@disagg_test_class`, transaction context helpers, `open_cursor`, `next`, `prev`, `search`, `remove`, `disagg_advance_checkpoint`, and timestamped commits. `_apply_ops` mutates leader or follower rows based on state letters, `_verify_zigzag` alternates scan directions, and `_verify_cursor` checks forward, backward, zigzag, and point reads.

Control flow: the leader creates one layered table per generated situation. Stable states are first inserted and checkpointed. Leader and follower remove `X` states, then the follower inserts ingest-visible rows and tombstones `R` states. After checkpoint advancement, the follower verifies each table.

State and persistence behavior: the file explicitly documents the stable/ingest/tombstone state machine and then creates those states with timestamped transactions and checkpoint handoff. The expected visible set is only `I`, `S`, and `B`. The same cursor must transition correctly from unpositioned state to data, across visible and hidden keys, and back to `WT_NOTFOUND`.

Dependencies and integration: relies on layered disaggregated table support, follower connections, precise checkpointing, and WiredTiger transaction helpers. Risks include combinatorial gaps in merge transitions, hidden tombstones appearing in scans, point search disagreeing with iteration, and infinite loops in zigzag iteration. Test signals are strict expected list equality, value equals key checks, `WT_NOTFOUND` assertions, and a loop guard in `_verify_zigzag`.
