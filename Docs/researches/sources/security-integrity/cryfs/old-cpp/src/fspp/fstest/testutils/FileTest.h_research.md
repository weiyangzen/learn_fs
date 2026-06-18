# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileTest.h

Purpose: file-specific fixture setup and assertion helpers shared by `FsppFileTest`.

Important APIs/types/functions: `FileTest`, constructor-created `file_root`, `file_nested`, node mirrors, `IN_STAT`, `EXPECT_SIZE`, `EXPECT_NUMBYTES_READABLE`, `EXPECT_ATIME_EQ`, and `EXPECT_MTIME_EQ`.

Control flow: constructor creates `/myfile`, `/mydir/mynestedfile`, and `/mydir2`. Assertions compare stat from both generic node and open-file views, then validate read length by reading one byte past expected size.

State and persistence behavior: fixture pre-populates root and nested file entries. Size assertions rely on persisted file data and metadata being visible through separate file and node handles.

Dependencies and integration points: inherits `FileSystemTest`; uses `cpputils::Data`, `unique_ref`, fspp file APIs, and typed byte-count wrappers.

Risks and test signals: strengthens file tests by checking both stat surfaces and actual readable byte count. Constructor state is broad and may mask tests that accidentally depend on preexisting `/mydir2`.
