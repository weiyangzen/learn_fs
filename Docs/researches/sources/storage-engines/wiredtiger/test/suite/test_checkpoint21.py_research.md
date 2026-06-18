# sources/storage-engines/wiredtiger/test/suite/test_checkpoint21.py

Purpose: tests checkpoint visibility for a committed prepared transaction whose commit timestamp is before stable but durable timestamp is after stable. It documents the chosen behavior that checkpoint cursors may show committed-but-not-yet-durable data in no-read-timestamp mode while timestamped reads follow timestamp visibility.

Important APIs and types: prepared transaction APIs, durable timestamp commit configuration, `debug=(release_evict)`, named/unnamed checkpoint helpers, and checkpoint cursor timestamp debug configuration.

Control flow: write initial data at timestamp 10; prepare full-table update at timestamp 20; advance stable to 30; commit at timestamp 25 with durable timestamp 35; evict half the pages; checkpoint while stable remains 30; then read the checkpoint at 15, 25, default, and no timestamp.

State and persistence behavior: half the transaction is forced to disk before checkpoint, and the remaining pages are checkpointed later. The core persistence question is whether checkpoint reconstructs a torn transaction consistently.

Dependencies and integration points: integrates timestamped visibility with prepared transaction persistence and checkpoint cursor read-time handling. Skipped for tiered and disaggregated hooks.

Risks: comments explain the semantics are pragmatic rather than obviously final. Any future change to default checkpoint read timestamp or durable timestamp visibility would need this test revisited.

Test signals: timestamped/default checkpoint reads see `value_a`, while no-read-timestamp checkpoint read sees all `value_b`, proving no torn transaction is observed.
