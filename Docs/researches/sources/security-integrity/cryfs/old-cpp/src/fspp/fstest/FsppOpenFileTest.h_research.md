# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest.h

Purpose: minimal typed tests for the `fspp::OpenFile` interface, focused on stat behavior for newly created files.

Important APIs/types/functions: `FsppOpenFileTest`, `IN_STAT`, `EXPECT_SIZE`, `EXPECT_NUMBYTES_READABLE`, `OpenFile::stat`, `OpenFile::read`, and `File::open`.

Control flow: creates a file, reopens it read-only, then asserts size and file mode through open-file stat. Readability helper attempts to read one byte past expected size and verifies exactly expected bytes are readable.

State and persistence behavior: no long-lived mutation beyond file creation; validates that open-file view reflects persisted file metadata and that empty files read as zero bytes.

Dependencies and integration points: inherits `FileSystemTest`; uses `cpputils::Data`, fspp byte-count wrappers, and typed GoogleTest registration for concrete backends.

Risks and test signals: only covers empty file stat and file-kind mode. TODOs list substantial missing coverage for open-file truncate/read/write/flush/fsync/fdatasync and create-and-open stat behavior.
