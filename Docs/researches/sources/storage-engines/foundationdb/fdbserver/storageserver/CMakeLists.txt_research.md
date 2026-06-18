# sources/storage-engines/foundationdb/fdbserver/storageserver/CMakeLists.txt

Purpose: defines the storage-server support library target and its tests.

Important APIs and functions: `fdb_find_sources(FDBSERVER_STORAGESERVER_SRCS)` gathers sources, `add_flow_target` builds `fdbserver_storageserver`, link and unit tests include core, kvstore, and logsystem dependencies, common include setup exports the public include path, and private local includes are enabled.

Control flow, state, and persistence: declarative build metadata only.

Dependencies and integration: storage-server utilities depend on `fdbserver_core`, key-value store abstractions, and logsystem pieces. The library is a modular subset around storage server helpers rather than the monolithic actor implementation.

Risks and test signals: risks are missing linkage when utilities use kvstore/logsystem types, public include path mistakes, and source discovery omissions. Successful library, link test, and `fdbserver_storageserver_test` build/run are the main signals.
