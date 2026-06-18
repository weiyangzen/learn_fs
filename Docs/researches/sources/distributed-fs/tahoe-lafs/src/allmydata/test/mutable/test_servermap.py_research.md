# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_servermap.py

## Purpose
This file tests mutable `ServermapUpdater` behavior across update modes, missing shares, corrupted-share marking, private-key fetching, and SDMF/MDMF discovery. It establishes how many shares each mode should query and how recoverable and unrecoverable versions are reported.

## Important APIs, Types, And Functions
`Servermap` inherits `AsyncTestCase` and `PublishMixin`. Helpers include `make_servermap`, `update_servermap`, `failUnlessOneRecoverable`, `failUnlessNoneRecoverable`, and `failUnlessNotQuiteEnough`. It uses `ServerMap`, `ServermapUpdater`, `Monitor`, `MutableData`, and modes `MODE_CHECK`, `MODE_WRITE`, `MODE_READ`, and `MODE_ANYTHING`.

## Control Flow
`setUp` publishes a default file. `test_basic` builds fresh maps in each mode and then reuses one map while increasing the query completeness from `MODE_ANYTHING` through read/write/check behavior. Other tests delete all shares, leave only two shares, mark shares as bad, publish MDMF or SDMF variants, request update data ranges, and check that private keys can be discovered for normal and larger mutable files.

## State, Persistence, And Dependencies
The file manipulates `self._storage._peers` directly, so state is in-memory and source-order sensitive. `ServerMap.mark_bad_share` changes map state, and follow-up updates must avoid already marked shares. `test_fetch_update` depends on `ServerMap.update_data` containing ten server entries with one version each when an MDMF update range is requested.

## Risks And Test Signals
These tests catch regressions in stop-early query modes, stale servermap reuse, bad-share suppression, fetch-private-key behavior, and correct distinction between no version and unrecoverable version. They are especially sensitive to Tahoe's `k=3,n=10` defaults in `PublishMixin`.
