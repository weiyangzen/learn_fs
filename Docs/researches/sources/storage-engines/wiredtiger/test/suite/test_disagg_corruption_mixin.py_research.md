# sources/storage-engines/wiredtiger/test/suite/test_disagg_corruption_mixin.py

Purpose: exercises `DisaggCorruptionMixin` helpers against palite-backed disaggregated storage to ensure corruption utilities mutate page-log rows as intended.

Important APIs and control flow: scenarios come from `gen_disagg_storages(..., disagg_only=True)`, but each test skips unless `ds_name == 'palite'`. `_populate` writes ten layered rows and checkpoints. Tests call mixin helpers to corrupt a page image, delete a page image, mark a page discarded, and truncate a delta chain; each then queries palite SQLite data with `sqlite_select_json`.

State and persistence: persistent state is palite `pages` rows, including `page_data`, `flags`, `discarded`, page IDs, LSNs, and delta chains.

Dependencies and integration: uses `DisaggCorruptionMixin`, disaggregated extension configuration, `make_scenarios`, and SQLite-backed palite inspection.

Risks and test signals: asserts byte `FF`, deleted row count zero, discarded flag mask set, and delta chain reduced to the kept LSN. Failures break corruption-test infrastructure.
