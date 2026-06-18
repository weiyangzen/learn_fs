# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor21.py

Purpose: regression coverage for `next_random` on layered tables when every reachable row is a tombstone. It targets WT-15189 behavior: return `WT_NOTFOUND` rather than spinning when all records are deleted.

Important APIs and functions: `test_layered_cursor21` uses `@disagg_test_class`, `@wttest.skip_for_hook("tiered", ...)`, URI scenarios for `layered:` and `table:` with `block_manager=disagg,type=layered`, follower setup through `setup_follower`, range deletion helpers `truncate_range` and `remove_range`, and `open_cursor(..., "next_random=true")`.

Control flow: tests create base data, advance checkpoint state to a follower, then delete all visible records either by truncate or per-row remove. Cases cover ingest-only tombstones and scattered tombstones split between stable and ingest. `assert_random_notfound` opens a random cursor and asserts the call returns `WT_NOTFOUND`.

State and persistence behavior: stable data can be empty or partially populated, while tombstones may live entirely in ingest or across stable/ingest after checkpoint advancement. Range truncation and per-key removes create different tombstone shapes but the final visibility set is empty.

Dependencies and integration: integrates layered random cursor selection, disaggregated storage, row-store table creation, timestamped deletes, truncation, and tiered-storage skip hooks. Risks include random cursor loops over invisible rows, tombstone density causing retry exhaustion bugs, and different behavior between `layered:` and `table:` URIs. Test signals are direct `WT_NOTFOUND` assertions for random lookup after each all-deleted setup.
