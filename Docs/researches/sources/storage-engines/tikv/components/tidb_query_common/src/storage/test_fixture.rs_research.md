# sources/storage-engines/tikv/components/tidb_query_common/src/storage/test_fixture.rs

## Purpose
Provides `FixtureStorage`, a test-only `Storage` implementation backed by an in-memory `BTreeMap<Vec<u8>, FixtureValue>`. It lets storage executor tests read deterministic key/value fixtures and inject per-key storage errors.

## APIs, Flow, And State
Important public pieces are `ErrorBuilder`, `FixtureValue`, `FixtureStorage::new`, conversions from byte-slice fixtures and `Vec<(Vec<u8>, Vec<u8>)>`, and the `Storage` trait methods `begin_scan`, `scan_next_entry`, `get_entry`, `collect_statistics`, and `met_uncacheable_data`. `begin_scan` creates a sorted map range from an `IntervalRange`, records direction and key-only flags, and stores an iterator with an erased lifetime. `scan_next_entry` advances from the front or back, clones returned keys/values, emits empty values for key-only scans, and calls the stored error builder for fixture errors. `get_entry` does point lookup by `PointRange`.

## Dependencies And Integration
Depends on the sibling storage range types, `OwnedKvPairEntry`, and the `Storage` trait. It integrates with unit tests and executor tests that need a simple source compatible with production storage APIs.

## Risks And Test Signals
The core risk is the unsafe transmute used to keep a `BTreeMap::Range` inside a self-referential storage object. It is acceptable only because the map is owned through `Arc` and results are cloned, but misuse around cloning or replacing `data` would be high risk. Tests cover point lookups, forward/backward scans, key-only mode, cloning mid-scan, and empty ranges.
