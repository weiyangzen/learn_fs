# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp

## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp

Purpose: Implementation of a lightweight mock `WT_CONNECTION_IMPL` owner for tests that do not require a real WiredTiger home.

Important functions: `build_test_mock_connection` allocates zeroed `WT_CONNECTION_IMPL`, constructs `mock_connection`, and initializes stats. Destructor frees block/file hash arrays, destroys block lock if initialized, discards connection stats, and frees the connection. `setup_block_manager` initializes checksum, block/file hash tables and queues, spin locks, home path, and OS file-system layer. `setup_stats` initializes connection stats and flags and sets `default_session`.

State and persistence: in-memory connection internals only. Optional file-system layer can be initialized for block manager tests but does not open a real database.

Dependencies/integration: used by `mock_session` and tests needing internal connection fields. Depends on WT allocation, stat, spin, crc, and OS abstraction helpers. Risks include partial cleanup of initialized locks (`fh_lock` is initialized but destructor only checks `block_lock`), null-session allocation/free assumptions, and drift with `WT_CONNECTION_IMPL` layout. Test signals are indirect through mock-backed internal API calls.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_connection.cpp -->
