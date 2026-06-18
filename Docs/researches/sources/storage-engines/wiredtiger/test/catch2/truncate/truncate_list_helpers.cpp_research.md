# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp

Purpose: Shared helper implementation for layered truncate-list tests.

Important functions/types: `make_item`, `as_view`, `truncate_list_head`, `truncate_list_size`, `lock_is_released`, `last_txn_op`, and `truncate_list_fixture`. The fixture owns a mock session, `WT_LAYERED_TABLE`, truncate queue, and truncate rwlock.

Control flow: `make_item` creates a shallow `WT_ITEM` view over a `std::string_view`; `as_view` reverses that view. `truncate_list_size` iterates `TAILQ_FOREACH`. `lock_is_released` attempts a write lock and releases it on success. The fixture constructor initializes table name, queue, and lock. Destructor drains any remaining entries, releases the dhandle reference if data existed, and destroys the lock. `add_entry` allocates `WT_TRUNCATE`, acquires a dhandle reference only for first entry, shallow-copies keys, inserts at tail, and checks size. `commit_entry` builds a temporary `WT_TXN` and applies commit stamping.

State and persistence: purely in-memory helper state. Key storage is shallow and assumes string literals/static lifetimes unless callers use copied buffers.

Dependencies/integration: underpins all truncate list unit tests and wraps production functions `__wti_mark_committed_truncate_table_apply` and lock/reference macros. Risks include reference accounting assumptions and shallow-key lifetime. Test signals are helper `CHECK`/`REQUIRE` assertions plus caller checks.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.cpp -->
