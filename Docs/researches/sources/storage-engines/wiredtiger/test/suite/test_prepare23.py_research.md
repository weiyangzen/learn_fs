# sources/storage-engines/wiredtiger/test/suite/test_prepare23.py

## Purpose

Stresses prepare rollback with rollback-to-stable under a failed eviction split timing stress.

## Important APIs, Control Flow, and State

With `timing_stress_for_test=[failpoint_eviction_split]`, the test loops 1000 keys, each with value A, value B, optional delete, and a prepared value C. For each key it evicts using `ignore_prepare=true` at the B timestamp, rolls back the prepare, advances stable to the last committed timestamp, calls `rollback_to_stable`, and verifies A/B plus optional deletion remain readable. The timestamp base increments per key to avoid cross-key timestamp reuse.

## Dependencies, Risks, and Test Signals

Dependencies are failpoint eviction split, timestamped updates/removes, rollback-to-stable, and scenarios. The risk is failed eviction paths leaving prepared rollback state that RTS misinterprets. Signals are repeated per-key verification over 1000 iterations.
