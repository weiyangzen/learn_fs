# sources/storage-engines/wiredtiger/test/suite/test_prepare25.py

## Purpose

Covers a rollback of one prepared update followed by a committed prepared update on the same key under eviction failure stress.

## Important APIs, Control Flow, and State

Each of 1000 keys receives value A, optional delete, a prepared value B that is evicted and rolled back, then a second prepared value C that commits with durable timestamp after the commit timestamp. A second eviction occurs after commit. Reads verify A at the first timestamp, optional deletion at the delete timestamp, and C at the second prepare/commit timestamp. The connection uses `timing_stress_for_test=[failpoint_eviction_split]`.

## Dependencies, Risks, and Test Signals

Dependencies are prepared rollback/commit sequencing, eviction failpoint, scenario key formats, and timestamp visibility. The risk is stale rollback state from the first prepared update interfering with the later committed prepared update. Signals are long repeated key coverage and post-resolution reads.
