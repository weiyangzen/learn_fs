# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_repairer.py

## Purpose
Tests immutable file checking, verification, and repair using the no-network grid. It validates corruption judgments, repair after deletion, operation-count budgets, server response reporting, and documents known repairer limitations.

## APIs / Types / Functions
- `RepairTestMixin` counts reads/allocates/writes, stashes deltas, and uploads shared data.
- `Verifier` tests `filenode.check(Monitor(), verify=...)`.
- `Repairer` tests `filenode.check_and_repair(Monitor(), verify=...)`.
- Judgment helpers inspect `CheckResults` for healthy, corrupt, incompatible, and missing-share states.
- Constants define leeway thresholds for read/write regression detection.

## Control Flow
Verifier tests upload data, optionally corrupt or delete shares, run check/verify, enforce read budgets, and assert result fields such as good shares, sharemaps, servers responding, corrupt shares, and incompatible shares. Repairer tests validate harness behavior, repair one or seven deleted shares, verify restored health and filesystem share count, prove downloads survive further deletion, repair with reduced server happiness, detect tiny-read regressions, and ensure post-repair server-response lists include repair responders.

## State And Persistence
Creates real no-network storage directories and immutable share files. Tests delete/corrupt shares, remove servers, inspect server counters, and store URIs/filenodes/counter snapshots on the test instance.

## Dependencies / Integration Points
Integrates immutable upload/download, `Monitor`, `check_results`, no-network grid share helpers, storage counters, corruption helper functions, and `NotEnoughSharesError`.

## Risks And Test Signals
The disabled `OFF_test_repair_from_corruption_of_1` documents major known limitations: minimal verifier coverage, download failure when share switching should occur, inability to delete corrupt immutable shares through the storage API, and possible lost-progress bugs. Passing tests signal verifier accounting correctness, bounded repair cost, restored downloadability, accurate response reporting, and avoidance of pathological tiny reads.
