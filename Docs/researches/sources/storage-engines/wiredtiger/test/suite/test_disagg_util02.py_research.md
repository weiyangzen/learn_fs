# sources/storage-engines/wiredtiger/test/suite/test_disagg_util02.py

Purpose: tests the diagnostic `wt page` command against palite-backed disaggregated storage, covering help, validation errors, full page images, and delta chains.

Important APIs and types: `PalitePage` is a `NamedTuple` matching palite page table fields. `test_disagg_wt_page` configures a leader layered table, computes page-log follower config, runs `wt page`, populates rows, dirties subsets, and queries palite SQLite via the built `sqlite3`.

State and persistence: page-log state includes table IDs, shard DBs, page IDs, LSNs, base/backlink LSNs, and flags. The command output is validated against these stored page-chain headers.

Dependencies and integration: uses `DisaggConfigMixin`, `get_shard_id`, `get_table_id`, `wt_builddir`, `suite_subprocess`, `wiredtiger.diagnostic_build()`, and skips tiered hooks.

Risks and test signals: diagnostic builds only. It asserts required argument errors, `WT_NOTFOUND`, full-image count 1 with row-store output, and delta-chain count greater than 1.
