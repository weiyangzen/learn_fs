<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json

Purpose: fixture data loaded into `WT_HOME_COVERAGE` during coverage setup so later `wt` utility commands can operate on a known table.

Data contract: JSON uses `WiredTiger Dump Version` and a `table:test_table` array containing metadata/config and data entries. The table config defines a file-backed btree with string key/value formats, logging enabled, checksum on, and source `file:test_table.wt`. The data section inserts two simple string-key/string-value records.

State and persistence: consumed by `./wt -h WT_HOME_COVERAGE load -j -f ../test/evergreen/code_coverage/test_table.json`, which creates persistent WiredTiger table data in the coverage home.

Dependencies and integration: referenced directly from `code_coverage_config.json` setup actions. Later coverage commands exercise utility operations such as list, dump, verify, alter, write, and drop against `test_table`.

Risks and test signals: format must remain compatible with the `wt load -j` JSON dump parser and WiredTiger version expectations. Changes to table config can alter utility coverage and behavior. Because coverage tasks run destructive `wt` commands, setup copies isolate this fixture per build directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json -->
