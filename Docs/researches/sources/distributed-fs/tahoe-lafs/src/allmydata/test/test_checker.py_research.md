# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_checker.py

## Purpose
This file tests checker and repair result rendering, good-share-host accounting, add-lease failure tolerance, and immutable verifier parallelism. It spans web result HTML/JSON rendering and actual no-network grid behavior.

## Important APIs, Types, And Functions
Fake support types include `FakeClient`, `FakeServer`, `FakeCheckResults`, `FakeCheckAndRepairResults`, `ElementResource`, `CounterHolder`, and `MockVRBP`. Test classes are `WebResultsRendering`, `BalancingAct`, `AddLease`, and `TooParallel`. The file exercises `check_results.CheckResults`, `CheckAndRepairResults`, `DeepCheckResults`, `DeepCheckAndRepairResults`, web renderer elements/resources, `StorageFarmBroker`, `NativeStorageServer`, `GridTestMixin`, immutable `Data`, mutable `MutableData`, and `ValidatedReadBucketProxy`.

## Control Flow
Rendering tests build fake result objects and storage brokers, render Twisted web elements through `render` or `renderElement`, parse HTML with BeautifulSoup, and verify exact user-facing labels plus JSON payload structure. Grid tests upload data, manipulate share placement or server behavior, run `check_and_repair` or `check`, and inspect counters. `TooParallel` monkeypatches `allmydata.immutable.checker.ValidatedReadBucketProxy` to count active block fetches and restores it in `addBoth`.

## State, Persistence, And Dependencies
Web tests are mostly in-memory. Grid tests persist real share files in no-network storage directories and copy/delete shares by storage index path. `BalancingAct` uses a custom topology to differentiate good share count from good host count. `AddLease` mutates a live storage server's `add_lease` method to raise.

## Risks And Test Signals
This file catches UI/API compatibility regressions in check result rendering, false checker negatives when lease renewal fails, incorrect happiness/good-host metrics, and memory-risk regressions from overly parallel verification. Monkeypatch cleanup is critical; failure before restoration would affect later tests, though the `addBoth` cleanup mitigates this.
