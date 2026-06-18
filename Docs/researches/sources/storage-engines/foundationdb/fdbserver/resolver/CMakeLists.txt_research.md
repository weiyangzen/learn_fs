# sources/storage-engines/foundationdb/fdbserver/resolver/CMakeLists.txt

Purpose: declares the `fdbserver_resolver` static library and its validation targets.

Important APIs and functions: `fdb_find_sources(FDBSERVER_RESOLVER_SRCS)` collects sources, `add_flow_target` builds the library, link and unit tests include `fdbserver_logsystem` and `fdbserver_core`, common includes are configured, the public `include` directory is exported, and local source directory is private.

Control flow, state, and persistence: declarative build metadata only. It defines no runtime behavior or persistent state.

Dependencies and integration: resolver depends on core server interfaces and the logsystem because resolver private mutations can use a log-system-backed key-value store. This target is consumed by fdbserver role recruitment and tests.

Risks and test signals: risks are missing logsystem linkage, hidden include path mistakes, and source discovery omissions. Build signals are successful resolver library, link test, and resolver unit-test target.
