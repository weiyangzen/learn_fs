# sources/user-network-fs/nfs-ganesha/src/gtest/gtest.hh

## Purpose
This header provides the shared C++ GoogleTest harness for Ganesha FSAL integration tests. It starts and stops a real Ganesha server thread, creates a per-test export root directory, initializes operation context, provides bulk file creation/removal helpers, and optionally controls LTTng trace events.

## Important APIs, Types, And Functions
`gtest::Environment` wraps `nfs_libmain` in `std::thread`, calls `admin_halt` on destruction, and stores LTTng session, test root name, and export id. `GaneshaBaseTest` provides `enableEvents` and `disableEvents` for all or comma-selected tracepoints. `GaneshaFSALBaseTest` creates `root_entry`, `test_root`, `req_op_context`, and default `fsal_attrlist attrs`; it also defines `create_and_prime_many`, `remove_many`, and `readdir_callback`. The macro `gtws_subcall` temporarily switches `op_ctx->fsal_export` to a stackable sub-export.

## Control Flow, State, And Persistence
Environment construction starts Ganesha and sleeps five seconds for initialization. Fixture setup obtains the configured export, root entry, initializes a simple op context, prepares default owner/group/mode attributes, and creates the named test root directory. Teardown unlinks the test root, releases object references, clears export pointers, and releases op context. Bulk creation uses `fsal_create` and primes cache with `fsal_readdir`; removal releases optional object references before `fsal_remove`.

## Dependencies And Integration Points
The header bridges C++ tests with C Ganesha headers, liburcu, LTTng control APIs, gperftools, NFS export management, and FSAL operations. It is included by most FSAL latency tests and by `gtest_nfs4.hh`.

## Risks And Test Signals
`gtest::Environment* env` is defined in the header, which can be fragile if included in multiple translation units for one executable. The startup sleep is a fixed timing assumption. `create_and_prime_many` does not assert the final priming `fsal_readdir` status. The helper centralizes cleanup, so failures here affect all dependent tests.
