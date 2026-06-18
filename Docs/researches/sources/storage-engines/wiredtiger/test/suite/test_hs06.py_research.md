# sources/storage-engines/wiredtiger/test/suite/test_hs06.py

## Purpose

Large collection of history-store read regressions covering direct HS reads without memory spikes, modify reconstruction, prepared updates, same-timestamp updates, multiple modifies, instantiated modifies, and reconciliation of modifies from HS.

## Important APIs, Types, and Functions

Defines `test_hs06` with helpers `get_stat`, `get_non_page_image_memory_usage`, and `create_key`, and eight test methods using `wiredtiger.Modify`, checkpoint cursors, prepared transactions, and read timestamps.

## Control Flow

The methods create timestamped full values and modify chains, checkpoint/evict them into history store, then read historical versions. Some tests read checkpoints at explicit debug timestamps, some verify prepare conflicts or between commit/durable reads, and others force cache pressure with an extra table before reading reconstructed values.

## State and Persistence Behavior

State includes data-store page images, HS full updates and reverse deltas, prepared updates, same-timestamp update chains, stable/oldest timestamps, and memory usage stat `cache_bytes_other`.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, fast stats, scenario key formats, checkpoint cursor debug config, prepared transaction APIs, and cache pressure from small caches.

## Risks and Maintenance Signals

The memory-spike assertion uses a loose doubled threshold. Comments contain old `las` terminology. Workloads are heavy and rely on eviction/checkpoint behavior rather than direct HS inspection.

## Test Signals

Signals are exact historical values at timestamps, prepare conflict exceptions, successful read between commit/durable timestamps, and bounded non-page memory growth.
