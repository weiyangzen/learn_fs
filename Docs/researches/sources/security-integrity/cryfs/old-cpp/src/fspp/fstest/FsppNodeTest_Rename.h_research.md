# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Rename.h

Purpose: node-generic rename behavior tests run against file, directory, and symlink nodes. It covers success paths, overwrite behavior, error propagation, and validity of a node object after repeated renames.

Important APIs/types/functions: `FsppNodeTest_Rename`, `Node::rename`, `Device::Load`, `Dir::children`, `FuseErrnoException`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: `REGISTER_NODE_TEST_SUITE` expands the same `Test_*` methods into file-node, dir-node, and symlink-node typed fixtures. Tests create source and target trees, execute rename, then assert loadability or expected errno values.

State and persistence behavior: rename moves directory entries and may replace existing nodes. Error tests assert that original nodes remain loadable, while overwrite count tests ensure replaced entries do not duplicate directory children.

Dependencies and integration points: depends on `FsppNodeTest`, `FileSystemTest`, `boost::none`, and FUSE errno translation via `fspp::fuse::FuseErrnoException`.

Risks and test signals: covers `ENOENT`, `ENOTDIR`, `EBUSY`, `EISDIR`, cross-directory moves, self-renames, and replace semantics. TODOs identify missing invariant checks for stat fields and contents across rename success and failure paths.
