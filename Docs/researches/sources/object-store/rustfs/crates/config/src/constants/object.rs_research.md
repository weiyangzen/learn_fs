<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/object.rs -->
# sources/object-store/rustfs/crates/config/src/constants/object.rs

## Purpose
Defines object read/write performance, timeout, buffering, lock, backpressure, priority scheduling, storage-media detection, and adaptive read-ahead environment constants.

## Important APIs, types, and functions
Important knobs cover high/medium concurrency thresholds, max disk reads, optional GetObject bitrot skip, fixed and dynamic GetObject/disk-read timeouts, duplex and I/O buffer sizes, lock optimization and diagnostics, deadlock detection, backpressure watermarks, I/O priority thresholds and queue capacities, starvation prevention, load sampling, storage media override/detection, access-pattern history, bandwidth EMA thresholds, media-specific buffer caps, and random read-ahead disablement.

## Control flow
No local control flow. Runtime object APIs consume these constants while calculating timeouts, buffer sizes, priority classes, lock diagnostics, and adaptive I/O behavior.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with S3 GetObject paths, erasure/disk reads, namespace lock managers, priority I/O schedulers, backpressure controllers, storage-media probes, and bitrot verification.

## Risks and edge cases
This file controls many performance and safety defaults; mismatches between comments and parser validation can create dangerous operator assumptions. Skipping bitrot verification is security/integrity-sensitive. Large buffers and queues can multiply memory use under concurrency. Deadlock diagnostics are off by default and must not become a hot-path cost unexpectedly.

## Test signals
Tests should cover timeout calculation bounds, priority classification and starvation promotion, lock diagnostic thresholds, bitrot verification toggles, storage-media overrides, and memory behavior under high concurrency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/object.rs -->
