# sources/user-network-fs/samba/source3/torture/test_idmap_tdb_common.c

Purpose: This file is a comprehensive unit-style test for idmap TDB common allocation and mapping code. It validates high-water-mark allocation, SID/unixid mapping creation, one-to-one constraints, batch lookup status codes, read-only behavior, and range exhaustion.

Important APIs/types/functions: The file defines stub winbind functions (`find_domain_from_name()`, `get_global_winbindd_state_offline()`, `winbindd_use_idmap_cache()`) so idmap code can run locally. `open_db()` creates `idmap_test.tdb` under `lp_private_dir()` and initializes `GROUP HWM` and `USER HWM` to `LOW_ID`. `idmap_test_tdb_db_init()` installs `idmap_tdb_common_get_new_id()` and `idmap_tdb_common_set_mapping()` in an `idmap_rw_ops`. `createdomain()` builds an `idmap_domain` with low/high range 100..199. `run_idmap_tdb_common_test()` sequences all checks.

Control flow: The test initializes a domain and database, allocates a single id, sets valid UID and GID mappings while rejecting invalid parameters and SID/type conflicts, tests single SID-to-unixid and unixid-to-SID lookups, tests batch `sids_to_unixids()` and `unixids_to_sids()` including NONE_MAPPED/SOME_UNMAPPED/OK statuses, toggles `dom->read_only` for status-only lookup behavior, and finally consumes the remaining id range to ensure allocation fails when exhausted.

State/persistence behavior: Persistent state is in `idmap_test.tdb`: high-water-mark keys and bidirectional mapping records. Tests share one domain/database across the sequence, so earlier mappings are intentionally reused by later batch lookup status tests. The file does not explicitly unlink the database.

Dependencies and integration points: It integrates with winbind idmap headers, dbwrap TDB open APIs, domain SID helpers, idmap RW methods, and Samba private-dir configuration. It tests the common backend code used by idmap TDB implementations.

Risks: Because state accumulates across test functions, order matters; `CHECKRESULT` short-circuits on first failure. Existing database contents or previous partial runs can affect high-water marks unless the private test database is reset externally. Range exhaustion is deterministic only with the configured `LOW_ID`/`HIGH_ID`.

Test signals: Passing requires exact NTSTATUS values for invalid parameters, conflict rejection, out-of-range lookup rejection, mapping-state statuses, successful round-trip equality with `dom_sid_equal()`, nonzero allocated ids within range, and final allocation failure after the pool is depleted.
