# sources/storage-engines/wiredtiger/test/suite/test_tiered11.py

## Purpose
`test_tiered11.py` verifies that tiered metadata records the checkpoint flush timestamp and a nonzero flush time for both tiered and object URIs.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `metadata:` cursors, `timestamp_str`, and `conn.set_timestamp`. `add_data(start)` writes ten records with spaced commit timestamps and advances oldest/stable to the last logical stable timestamp.

## Control Flow
The test creates an integer tiered table, calls `add_data(1)`, checkpoints, then calls `add_data(nentries)` to advance the stable timestamp after the checkpoint. It then performs `checkpoint('flush_tier=(enabled)')`, performs another normal checkpoint, and checks metadata for the tiered URI and first object URI.

## State and Persistence Behavior
The key persistence behavior is that a flush records the stable timestamp of the checkpoint being flushed, not a later stable timestamp set after that checkpoint. Metadata also stores `flush_time`, which must not remain zero.

## Dependencies and Integration Points
It integrates tiered flush metadata with WiredTiger timestamp management and metadata cursor inspection.

## Risks and Test Signals
The risk is recording the wrong stable timestamp when stable advances between checkpoint and flush. Signals are metadata containing `flush_timestamp="<end_ts>"` and not containing `flush_time=0` for both `tiered:` and `object:` URIs.
