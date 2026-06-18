# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Stat.h

Purpose: typed stat tests for generic nodes plus node-kind-specific stat assertions for files, directories, and symlinks.

Important APIs/types/functions: `FsppNodeTest_Stat`, `FsppNodeTest_Stat_FileOnly`, `FsppNodeTest_Stat_DirOnly`, `FsppNodeTest_Stat_SymlinkOnly`, `Node::stat`, and `mode_t` flag checks.

Control flow: generic node tests run via `REGISTER_NODE_TEST_SUITE`; file-only, dir-only, and symlink-only suites directly create typed nodes and inspect `Node::stat_info`.

State and persistence behavior: tests create nodes and immediately load/stat them. They verify nlink, size, and mode-kind bits, without mutating persistent content beyond fixture setup.

Dependencies and integration points: uses `FsppNodeTest`, `FileSystemTest`, `FsppNodeTestHelper::IN_STAT`, and concrete fixtures supplied through typed-test instantiation.

Risks and test signals: provides basic stat contract signals but intentionally shallow coverage. TODO notes more stat cases are needed, such as permissions, ownership, timestamps, and potentially link counts for directories.
