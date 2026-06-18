# sources/storage-engines/wiredtiger/test/suite/test_checkpoint20.py

Purpose: verifies reading checkpoint data when the checkpoint contains prepared updates. The intended behavior is that checkpoint cursors use ignore-prepare semantics and expose stable prior values rather than failing on prepared conflicts.

Important APIs and types: prepared transactions (`prepare_transaction`, `timestamp_transaction`, durable commit), `SimpleDataSet`, debug eviction cursors `debug=(release_evict)`, named/unnamed checkpoints, and checkpoint read timestamps.

Control flow: write stable data at timestamp 10; prepare updates over half the table at prepare timestamp 20; evict pages while reading at timestamp 10 so prepared content is written; checkpoint with stable timestamp either 15 or 25; commit prepared data later; then read checkpoint at timestamps 10, 20, and default.

State and persistence behavior: the checkpoint can contain pages with prepared data, but the checkpoint cursor should reconstruct the visible stable state. Eviction forces prepared updates to disk before checkpoint to exercise on-disk prepare handling.

Dependencies and integration points: depends on transaction prepare/durable timestamp semantics, eviction debug cursors, checkpoint cursor visibility, and scenario coverage over row/column stores plus named/unnamed checkpoints.

Risks: the disabled `checkfail` path documents older conflict expectations but is not active. The test is sensitive to eviction effectiveness because without writing prepared pages the main edge case may not be reached.

Test signals: all checkpoint reads return exactly `value_a` for every row, including reads at timestamp 20 and default checkpoint read timestamp.
