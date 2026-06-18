# sources/storage-engines/foundationdb/fdbserver/tlog/CMakeLists.txt

Purpose: Defines the `fdbserver_tlog` static library, link test, and unit test target for transaction-log server components.

Important APIs/types/functions: Uses `fdb_find_sources(FDBSERVER_TLOG_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_tlog ...)`, `add_fdbserver_link_test(fdbserver_tloglinktest fdbserver_tlog fdbserver_logsystem fdbserver_core)`, `add_fdbserver_unit_test(fdbserver_tlog_test tlog ...)`, `configure_fdbserver_common_includes`, public/private include directories, and private links to `fdbserver_core`, `fdbserver_kvstore`, and `fdbserver_logsystem`.

Control flow: CMake discovers tlog sources, creates the library, configures tests and includes, and links the required internal libraries.

State and persistence behavior: Build graph only; no runtime state. The linked components themselves handle transaction-log persistence outside this file.

Dependencies and integration points: Integrates tlog sources with core, kvstore, and logsystem libraries. The unit test target gives a focused test lane named `tlog`.

Risks: Source discovery via `fdb_find_sources` can include unintended files. Missing private include for the current directory would break internal headers. Link target changes in core/logsystem/kvstore must be mirrored here.

Test signals: `fdbserver_tloglinktest` verifies link closure; `fdbserver_tlog_test` runs tlog unit tests.
