# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/expirer.py

## Purpose
Implements `LeaseCheckingCrawler`, a storage crawler that examines share leases, records expiration/recovery statistics, and optionally cancels expired leases to reclaim storage.

## Important APIs, Types, and Functions
Defines `_convert_pickle_state_to_json()`, `_HistorySerializer`, and `LeaseCheckingCrawler`. Important methods include `create_empty_cycle_dict()`, `process_bucket()`, `process_share()`, `add_lease_age_to_histogram()`, `finished_cycle()`, and `get_state()`.

## Control Flow
For each bucket, `process_bucket()` stats the bucket dir, iterates numeric share files, calls `process_share()`, records corrupt shares for unknown container/struct errors, and accumulates bucket-level recovery predictions. `process_share()` loads immutable/mutable share files via `get_share_file()`, evaluates each lease against original expiry and configured age/cutoff policy, optionally cancels expired leases, and returns booleans indicating whether original/configured/actual policies would keep the share.

## State and Persistence Behavior
Uses the base crawler JSON state for cycle-to-date data and `_HistorySerializer` for `lease_checker.history.json`, retaining the last 10 cycles. Cycle state includes corrupt shares, histograms, expiration mode, and recovered/examined bucket/share byte counters split by mutable/immutable. Actual deletion happens through `sf.cancel_lease()` when `expiration_enabled` is true and all configured-valid leases are gone.

## Dependencies and Integration Points
Depends on `ShareCrawler`, `get_share_file()`, unknown container exceptions, Twisted logging, `FilePath`, and share lease APIs. Storage web status pages consume `get_state()` output.

## Risks and Edge Cases
Lease-age mode uses original expiration time unless override duration is configured, which is subtle. `sharetype` for a bucket is derived from the last processed share. Corrupt shares are logged and counted but not repaired. Windows may lack `st_blocks`; code falls back to share bytes or zero bucket disk bytes. Expiration is destructive when enabled.

## Test Signals
`src/allmydata/test/test_storage_web.py` exercises lease checker status/rendering and no-`st_blocks` behavior; storage tests cover underlying lease cancellation and share-file semantics.
