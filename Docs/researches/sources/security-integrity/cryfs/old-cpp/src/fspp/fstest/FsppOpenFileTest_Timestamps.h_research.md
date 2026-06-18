# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest_Timestamps.h

Purpose: timestamp behavior tests for `fspp::OpenFile` operations, including stat, truncate, read, write, flush, fsync, and fdatasync.

Important APIs/types/functions: `FsppOpenFileTest_Timestamps`, `CreateAndOpenFile`, `CreateAndOpenFileWithSize`, `OpenFile`, `OpenFile::read`, `write`, `truncate`, `flush`, `fsync`, `fdatasync`, and `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS`.

Control flow: helper methods create files and open them `RDWR`; tests capture an `OpenFile*` plus a move-owned closure and evaluate expected timestamp changes under each atime mode. Read tests vary atime relative to mtime and whether reads are in bounds or partially beyond requested range.

State and persistence behavior: open-file truncation changes size and mtime/ctime; reads may update atime depending on context; writes update mtime/ctime; flush/fsync/fdatasync are expected timestamp-neutral after the preceding write.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest` atime-state setters, `std::array`, fspp open flags, and concrete filesystem fixture reset behavior.

Risks and test signals: strong matrix for relatime/noatime/nodiratime semantics on file reads. The "outofbounds" read cases still read from offset 2 in a 10-byte file for 5 bytes, so naming suggests intended boundary coverage may be incomplete.
