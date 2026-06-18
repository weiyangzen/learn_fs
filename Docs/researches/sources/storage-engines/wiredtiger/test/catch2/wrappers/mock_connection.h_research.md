# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h

## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h

Purpose: Header for `mock_connection`, an owned in-memory `WT_CONNECTION_IMPL`.

Important API: destructor, `get_wt_connection_impl`, `get_wt_connection`, static `build_test_mock_connection`, and `setup_block_manager`.

Control flow/state: class privately owns `_connection_impl` and exposes public/internal pointer views. Comments emphasize using mocks for speed when full connection behavior is unnecessary.

Dependencies/integration: includes `wt_internal.h` and is consumed by `mock_session`. Risks include exposing mutable internal connection state and consumers assuming more subsystems are initialized than the builder provides. Test signals are indirect through mock sessions and block-manager tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.h -->
