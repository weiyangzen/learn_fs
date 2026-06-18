# sources/storage-engines/wiredtiger/test/suite/test_compact05.py

Purpose: verifies foreground compaction honors `free_space_target`: it proceeds when available bytes exceed the threshold and skips with a warning when they do not.

Important APIs and types: `compact_util`, `make_scenarios`, `session.compact`, `expectedStdoutPattern`, `stat.dsrc.btree_compact_pages_rewritten`, and `btree_compact_pages_rewritten_expected`.

Control flow: create and populate a table, checkpoint, delete four large ranges, then compact with either `free_space_target=1MB` or `45MB`. For expected skip, capture stdout warning; otherwise compact normally and suppress verbose output. Finally inspect compact stats.

State and persistence behavior: compaction eligibility is based on tracked reusable bytes. Progress stats should remain zero when compaction is skipped before rewrite work.

Dependencies and integration points: foreground compaction threshold logic, compact verbose messages, and data-source statistics. Tiered hook is skipped.

Risks: exact available bytes must fall between 1MB and 45MB for the scenarios. Warning text is regex-matched and thus part of the contract.

Test signals: expected compaction yields positive rewritten and expected pages; expected skip yields zero for both.
