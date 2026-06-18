# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp

Purpose: Unit tests for truncate-list garbage collection via `__ut_layered_table_truncate_gc`.

Important helpers/APIs: `insert_durable_entry` creates an entry through `truncate_list_fixture::add_entry` and commits it through `commit_entry`, stamping durable timestamp. GC is called with a prune timestamp.

Control flow: scenarios cover zero prune timestamp no-op, uncommitted entries retained, entries with `WT_TS_NONE` durable timestamp retained, durable timestamp above prune retained, entries at or below prune removed, multi-entry lists with eligible/ineligible/uncommitted combinations, empty-list no-op, reference count unchanged when list remains non-empty, and reference count decremented exactly once when GC empties the list.

State and persistence: in-memory `WT_TRUNCATE` queue, committed flag/timestamps, and dhandle reference count. No disk persistence.

Dependencies/integration: focuses on internal eligibility rules: committed, nonzero durable timestamp, durable <= prune. Risks are timestamp boundary off-by-one bugs and reference leaks on partial/complete removal. Test signals are list size, head durable timestamp, and reference count.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_gc.cpp -->
