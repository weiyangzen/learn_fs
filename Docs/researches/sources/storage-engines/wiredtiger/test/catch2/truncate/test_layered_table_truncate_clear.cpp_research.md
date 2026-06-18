# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp

Purpose: Unit tests for `__wt_layered_table_truncate_clear`.

Important APIs/types: uses `truncate_list_fixture`, `truncate_list_size`, `reference_count`, and `lock_is_released` over a mock `WT_LAYERED_TABLE` containing a `truncateqh` queue and `truncate_lock`.

Control flow: scenarios build either a two-entry truncate list or an empty list, call clear, then assert all entries are removed, dhandle reference count is decremented exactly once only for non-empty lists, empty clear is a no-op, and the truncate write lock is not leaked.

State and persistence: purely in-memory list entries and reference counts. `truncate_list_fixture` handles lock initialization/destruction and any remaining entries.

Dependencies/integration: validates clear behavior without a real connection. It depends on helper fixture semantics that acquire a dhandle reference on the first entry. Risks include helper-created shallow keys and direct internal reference counting. Test signals are list size, reference count, and ability to acquire write lock after clear.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_clear.cpp -->
