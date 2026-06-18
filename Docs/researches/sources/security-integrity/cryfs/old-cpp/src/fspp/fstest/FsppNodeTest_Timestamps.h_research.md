# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Timestamps.h

Purpose: node-generic timestamp contract tests for files, directories, and symlinks. It covers creation, stat/access neutrality, chmod/chown/utimens ctime behavior, rename timestamp behavior, and rename error paths.

Important APIs/types/functions: `FsppNodeTest_Timestamps`, `Test_Create`, `Test_Stat`, `Test_Chmod`, `Test_Chown`, `Test_Access`, `Test_Rename_*`, `Test_Utimens`, `FuseErrnoException`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: tests build closures that mutate or inspect a node, then pass either one path or old/new paths into `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS`. Rename success compares old-path stat before with new-path stat after, while error paths compare the same path.

State and persistence behavior: exercises metadata stored in `Node::stat_info`; rename updates the node ctime but not atime/mtime; failed renames should leave timestamps unchanged. `utimens` explicitly changes atime/mtime and expects ctime to move to operation time.

Dependencies and integration points: mixes `FsppNodeTest` and `TimestampTestUtils`, requiring virtual inheritance through `FileSystemTest`. Uses fspp context atime policies and POSIX-like errno values.

Risks and test signals: broad cross-node timestamp coverage. Root-dir rename timestamp test is disabled because root timestamp storage is known incomplete; overwrite cases verify source node ctime but do not fully validate target deletion metadata side effects.
