# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest.h

Purpose: reusable typed tests for the `fspp::File` interface, covering open modes, truncation, ownership/mode mutation, explicit `utimens`, and removal for root and nested files.

Important APIs/types/functions: `FsppFileTest<ConcreteFileSystemTestFixture>`, `Test_Open_RDONLY`, `Test_Open_WRONLY`, `Test_Open_RDWR`, `Test_Truncate_*`, `Test_Chown_*`, `Test_Chmod`, `Test_Utimens`, `Remove`, and `REGISTER_TYPED_TEST_SUITE_P`.

Control flow: fixture members from `FileTest` provide root and nested file handles plus node handles. Tests call file or node methods, then assert through helper methods that node stat and open-file stat agree and readable size matches expected bytes.

State and persistence behavior: truncation grows and shrinks file content state; ownership, mode, and timestamps are persisted through `Node::stat`; removal verifies both generic `Load` and typed `LoadFile` return `boost::none`.

Dependencies and integration points: depends on `FileTest`, `fspp::File`, `fspp::Node`, `fspp::OpenFile`, typed GoogleTest registration, and fspp strongly typed wrappers such as `num_bytes_t`, `uid_t`, `gid_t`, and `mode_t`.

Risks and test signals: good basic contract coverage, but `Test_Open_RDWR` calls `RDONLY()` instead of `RDWR()`, likely weakening intended read-write mode coverage. TODOs note that some node-interface cases should move to node tests and that timestamp effects are covered elsewhere.
