<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py

Purpose: validates JSON statistics log output and `sources=[file:]` inclusion of table/file statistics.

Important APIs/types/functions: `test_stat_log02` manually opens connections, uses `glob`, `json.loads`, helper `check_stats_file`, `check_file_is_json`, and `check_file_contains_tables`. It creates a `table:foo` object and expects `file:foo.wt` in the JSON `wiredTigerTables` object when sources are enabled.

Control flow: `test_stats_log_json` opens with `statistics_log=(wait=1,json,on_close=1)`, closes to force output, then parses every line of the first stats file as JSON. `test_stats_log_on_json_with_tables` opens with JSON stats logging and file sources, creates/writes a table, closes, verifies JSON syntax, and searches for table source output.

State and persistence behavior: output state is the on-disk stats log. On-close ensures deterministic generation without waiting for periodic timing.

Dependencies/integration points: covers stats logging JSON encoder, source filtering, table-to-file source naming, and file globbing; tiered is skipped for the table-source case. Risks include only checking the first stats file and expected JSON key names; signals are parseable JSON and expected table source presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log02.py -->
