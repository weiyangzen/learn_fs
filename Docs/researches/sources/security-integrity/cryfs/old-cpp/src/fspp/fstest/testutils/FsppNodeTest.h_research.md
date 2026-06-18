# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FsppNodeTest.h

Purpose: macro and fixture infrastructure for writing one node test suite that runs against files, directories, and symlinks.

Important APIs/types/functions: `FsppNodeTestHelper`, `FsppNodeTest`, `CreateNode`, `_REGISTER_*_TEST_SUITE`, `REGISTER_NODE_TEST_SUITE`, and `INSTANTIATE_NODE_TEST_SUITE`.

Control flow: macros generate three derived fixture classes per test suite. Each derived class implements `CreateNode` by creating the appropriate node kind and loading it as a generic `fspp::Node`; Boost.Preprocessor expands each `Test_Name` method into a typed GoogleTest case.

State and persistence behavior: generated tests create concrete nodes through `FileSystemTest` helpers and then exercise generic node behavior against persisted backend state.

Dependencies and integration points: uses Boost.Preprocessor, GoogleTest typed tests, fspp node APIs, and virtual inheritance to combine helpers cleanly.

Risks and test signals: avoids duplicated file/dir/symlink tests, but macro expansion can obscure compile errors and makes registration order important. Create-node paths always create fresh nodes and do not cover preexisting-node collisions.
