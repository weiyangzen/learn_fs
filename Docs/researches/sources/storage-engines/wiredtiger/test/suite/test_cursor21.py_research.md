<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor21.py

Purpose: tests cursor reposition support and statistics under forced eviction/reposition stress.

Important APIs and control flow: scenarios cover column and integer-row formats with reposition debug mode enabled or disabled. `conn_config()` enables all stats and optionally `debug_mode=[cursor_reposition=true],timing_stress_for_test=(evict_reposition)`. The test inserts 9999 integer values, then in separate transactions scans with `next`, `prev`, `search`, and `search_near`, checking each value and reading `stat.conn.cursor_reposition` between phases. Reposition scenarios require the stat to increase; non-reposition scenarios require zero.

State, persistence, and dependencies: state includes table records, cursor position restoration after eviction stress, and connection statistics. Dependencies are `wiredtiger.stat`, transaction APIs, cursor navigation/search APIs, and timing stress configuration.

Integration points: covers cursor repositioning machinery during forward/backward/search traversal for row and column stores.

Risks and test signals: the test relies on stress hooks to trigger reposition consistently. Pass signals are correct values throughout traversal and reposition stat behavior matching the scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor21.py -->
