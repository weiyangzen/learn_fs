## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/checker.py

### Purpose
This module implements mutable-file health checking and check-and-repair orchestration. It builds a `ServerMap`, determines whether a mutable file is healthy/recoverable, optionally verifies all share bytes, reports corrupt shares, and invokes repair when appropriate.

### Important APIs, Types, and Functions
`MutableChecker` owns normal checks with `SERVERMAP_MODE = MODE_CHECK`. Its public `check(verify=False, add_lease=False)` returns a Deferred firing with `CheckResults`. Key helpers are `_got_mapupdate_results`, `_verify_all_shares`, `_process_bad_shares`, `_count_shares`, and `_make_checker_results`. `MutableCheckAndRepairer` subclasses it with `SERVERMAP_MODE = MODE_WRITE`, stores a `CheckAndRepairResults`, and overrides `check` to stash pre-repair results and call `_maybe_repair`.

### Control Flow
`MutableChecker.check` creates a fresh `ServerMap`, starts `ServermapUpdater` in check mode, optionally notifies history, and waits for the update. `_got_mapupdate_results` marks repair needed when there are unrecoverable versions, not exactly one recoverable version, or the best recoverable version has fewer than `N` distinct shares. If `verify=True`, `_verify_all_shares` runs `Retrieve(..., verify=True)` against the best version so data-level corruption is caught, then `_process_bad_shares` records failures and marks repair needed. `_make_checker_results` synthesizes human-readable report/summary strings, counters, share maps, corrupt share locators, server response lists, and a servermap copy into `CheckResults`.

`MutableCheckAndRepairer.check` runs the base check, stores pre-repair results, and `_maybe_repair` skips repair if not needed or if the node is read-only. Otherwise it calls `node.repair`, records success/failure, and builds post-repair results from the repairer servermap.

### State and Persistence Behavior
Checker state is per-operation: `bad_shares`, `need_repair`, `responded`, `_storage_index`, and `best_version`. It does not persist data itself. It may add leases through `ServermapUpdater(add_lease=True)` and repair can publish replacement shares through the node repair path.

### Dependencies and Integration Points
The module depends on `ServerMap`, `ServermapUpdater`, `Retrieve`, `CheckResults`, `CheckAndRepairResults`, `servers_of_happiness`, URI parsing, logging, and mutable common modes/errors. `MutableFileNode.check` and `check_and_repair` instantiate these classes. Repair integrates with `mutable/repairer.py`.

### Risks and Edge Cases
Lightweight `check` can miss corrupted block/share data because it trusts share metadata; full `verify=True` is required to download and validate bytes. Defaults for totally missing shares use arbitrary `k=3`, `N=10`, which can affect summary counters when no version exists. Sorting bad shares by `id` is deterministic only within a process. Read-only mutable files cannot be repaired here. The monitor is checked before expensive result creation and repair decisions, so cancellation depends on callers passing a live monitor.

### Test Signals
`test/mutable/test_checker.py` covers good files, no shares, insufficient shares, bad signatures, verify-vs-check differences for corrupted share data, corrupt share hash chains, encrypted private key failures, SDMF and MDMF behavior, and corrupt-share reporting. `test_deepcheck.py`, `test_checker.py`, and `test_repairer.py` exercise this through node-level check and check-and-repair APIs.
