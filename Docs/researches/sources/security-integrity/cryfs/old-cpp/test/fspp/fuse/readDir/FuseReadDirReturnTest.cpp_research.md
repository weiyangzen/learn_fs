# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirReturnTest.cpp

Purpose: This file tests fspp FUSE directory enumeration, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseReadDirTest.h, cpp-utils/pointer/unique_ref.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadDirReturnTest. Helper functions: LARGE_DIR, testDirEntriesAreCorrect. Direct tests: FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect; FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect_LargeDir1000; FuseReadDirReturnTest.DISABLED_ReturnedDirEntriesAreCorrect_LargeDir1000000.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory enumeration to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect; FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect_LargeDir1000; FuseReadDirReturnTest.DISABLED_ReturnedDirEntriesAreCorrect_LargeDir1000000. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
