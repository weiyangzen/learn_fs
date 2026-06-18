<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema07.py

Purpose: long-running cache pressure test ensuring repeated metadata create/drop activity does not fill a small cache.

Important APIs/types/functions: `test_schema07` uses `TieredConfigMixin`, `make_scenarios`, `wttest.longtest`, `session.create`, `session.open_cursor`, and `dropUntilSuccess`. Connection config sets `cache_size=10MB`.

Control flow: loop 20,000 times creating a unique table name, opening a cursor, inserting one key/value pair, closing the cursor, and dropping the table.

State and persistence behavior: this test repeatedly creates and destroys schema metadata and table files while relying on eviction/metadata cleanup to prevent the cache from remaining pinned. There is no final stats assertion; progress through all iterations is the signal.

Dependencies/integration points: integrates metadata cache behavior, table lifecycle, tiered storage scenario generation, and long-test scheduling. Risks include runtime cost and dependence on cache/metadata cleanup timing. Test signals are successful completion without cache stalls, rollbacks, or create/drop failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema07.py -->
