# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_page_log_handle.cpp

## Purpose
Tests disaggregated connection configuration for page-log handles, including optional key-provider page-log handle construction and destruction.

## Important APIs, Types, And Functions
Mock functions implement `WT_PAGE_LOG::pl_open_handle`, `terminate`, and `WT_PAGE_LOG_HANDLE::plh_close`. `setup_page_log_queue` allocates a mock `WT_PAGE_LOG`, wraps it in `WT_NAMED_PAGE_LOG`, and inserts it into `conn_impl->ext.pagelogqh`. Tests call `__wti_disagg_conn_config`, `__wti_disagg_destroy`, `__wti_conn_remove_page_log`, and `__wti_layered_table_manager_destroy`.

## Control Flow
The fixture builds a mock session/connection, initializes required spinlocks, installs the mock page log, and runs sections for handle construction without a key provider, construction with a dummy key provider, and destruction of preinstalled meta/key-provider handles. Cleanup removes page logs, destroys layered table manager state, and destroys locks.

## State And Persistence Behavior
All state is in the mock connection's disaggregated-storage fields and extension page-log queue. No durable page-log writes are performed.

## Dependencies And Integration Points
Depends on `mock_session`, `wiredtiger.h`, disaggregated storage configuration, page-log extension queues, spinlocks, and layered table manager cleanup.

## Risks And Edge Cases
The test expects `__wti_disagg_conn_config` to return `EINVAL` while still constructing certain handles, so it guards partial-initialization cleanup. It also catches missing key-provider handle creation when `conn_impl->key_provider` is set.

## Test Signals
Handle pointers must be non-null or null as expected, and destroy must null out `page_log_meta` and `page_log_key_provider`.
