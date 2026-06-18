# sources/storage-engines/sqlite/ext/misc/fuzzer.c

Purpose: implements the read-only `fuzzer` virtual table, which expands an input word into weighted rewrite variants from a backing rule table.

Important APIs/types/functions: `fuzzer_rule`, `fuzzer_stem`, `fuzzer_vtab`, and `fuzzer_cursor` model rewrite rules, active/output stems, table state, and scan state. Rule loading uses `fuzzerLoadRules()`, `fuzzerLoadOneRule()`, and `fuzzerMergeRules()`. Virtual table behavior is in `fuzzerConnect()`, `fuzzerBestIndex()`, `fuzzerFilter()`, `fuzzerNext()`, and `fuzzerColumn()`.

Control flow: connect loads and sorts four-column rule rows. Filtering initializes `word MATCH`, `distance`, and `ruleset` constraints. `fuzzerNext()` renders the current lowest-cost stem, creates successors, advances rewrite positions, suppresses duplicate outputs with a hash table, and maintains cost-ordered queues.

State and persistence: rules are cached in memory for the vtab lifetime; cursor queues, rendered buffers, and seen hashes are transient. The backing rule table is not watched for changes and the vtab writes nothing.

Dependencies/integration: SQLite virtual table APIs, planner constraints, prepared statements, and extension allocation APIs. Marked innocuous when connected.

Risks/test signals: unbounded expansion without `distance`/`LIMIT`, byte-length limits, memory growth, duplicate-cost correctness, and stale rules. Test malformed rules, cost/ruleset limits, empty rewrites, duplicate paths, sorted output, read-only behavior, and long string rejection.
