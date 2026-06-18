# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.cpp

Purpose: Implements a filesystem-backed statistic for total database file size.

Important APIs/types/functions: `collection_name_to_file_name` maps `table:name` to `DEFAULT_DIR/name.wt`. `get_file_names` collects all database collection files plus history store and metadata files. `get_db_size` sums `stat` sizes, allowing `ENOENT`. `check` fails if size exceeds configured max; `get_value` returns size as `int64_t`.

Control flow: metrics monitor invokes it without needing a WT statistics cursor. Windows currently logs that checking is not implemented but the implementation references a differently cased logger in the disabled block.

State and persistence: reads persistent WT files from disk; holds a database reference for collection names.

Dependencies/integration: depends on `database`, filesystem `stat`, WT internal file constants, logger, and `test_util`.

Risks and test signals: assumes table URIs map directly to `.wt` files under `DEFAULT_DIR`, which may not hold for all data sources or disaggregated layouts. Missing files are tolerated only as `ENOENT`; size-limit failures are fatal.
