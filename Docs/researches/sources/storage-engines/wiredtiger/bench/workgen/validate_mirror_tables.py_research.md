<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py -->
# sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py

Purpose: validates Workgen mirror table pairs in a WiredTiger home by comparing each base table with its mirror. Returns success only when all discovered mirror pairs match.

Important APIs and functions: `usage_exit`, `get_wiredtiger_db_files(connection)`, `get_mirrors(connection, db_dir, db_files)`, `get_mirror_file(metadata_cursor, filename)`, and `main(sysargs)`. It uses `py_common.wiredtiger_util.wiredtiger_open` and `wt_cmp_uri.wiredtiger_compare_uri`.

Control flow: parse one database directory argument; open WT readonly; enumerate metadata `file:` entries excluding WiredTiger internal files; for each file, inspect metadata for `app_metadata` keys `workgen_dynamic_table=true` and `workgen_table_mirror`; pair base and mirror files if both exist; close connection; compare each URI pair while redirecting comparator stdout to `/dev/null`; report success/failure count and exit accordingly.

State and persistence: readonly database access only. It opens `/dev/null` for suppressed comparator output and prints a summary.

Dependencies and integration: requires WiredTiger tools modules on `PYTHONPATH`. Integrates with Workgen dynamic table mirror testing and snapshot validation workflows.

Risks: `get_mirror_file` catches only `KeyError` by class name and may leave `metadata` undefined for other exceptions. App metadata parsing assumes comma-separated `key=value` entries without embedded commas/equal signs. `stdout` variable receives return value from `wiredtiger_compare_uri`, not captured output, because stdout is redirected. The URI strings include `db_dir/table:name`, matching comparator expectations but worth verifying if comparator API changes.

Test signals: process exit 0 on all mirror matches, exit 1 on usage or mismatches, and printed count of validated pairs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py -->
