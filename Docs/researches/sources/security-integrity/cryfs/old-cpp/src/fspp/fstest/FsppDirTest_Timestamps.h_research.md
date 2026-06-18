# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest_Timestamps.h

Purpose: typed GoogleTest timestamp coverage for `fspp::Dir` operations and directory-entry side effects across concrete filesystem fixtures. It validates that creating files, directories, and symlinks mutates the parent directory mtime/ctime but not atime, and that new children receive current atime/mtime/ctime values.

Important APIs/types/functions: `FsppDirTest_Timestamps`, `FsppDirTest_Timestamps_Entries`, `createAndOpenFile`, `createDir`, `createSymlink`, `children`, `remove`, `rename`, `REGISTER_TYPED_TEST_SUITE_P`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: each test builds an operation closure, resets the fixture through `TimestampTestUtils::testBuilder`, runs the closure under all atime policies, and compares pre/post `stat_info` timestamps. Child-entry tests inherit `FsppNodeTest` to run file, directory, and symlink variants.

State and persistence behavior: tests create transient directory trees through the abstract `Device`; timestamps are persisted in node metadata and reloaded with `Load`. Root-directory timestamp cases are deliberately commented out due known root timestamp handling gaps.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest`, `FsppNodeTest`, `cpputils::time`, and fspp directory APIs. It integrates with concrete fspp backends via typed-test instantiation.

Risks and test signals: strong coverage of POSIX-like timestamp semantics for directory mutations and listing, including noatime/strictatime/relatime/nodiratime behavior. Known risk is disabled root-directory coverage, which leaves `/` timestamp behavior unguarded.
