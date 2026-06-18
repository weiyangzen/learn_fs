# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnMtimeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h, cpp-utils/system/stat.h. Classes/fixtures: FuseLstatReturnMtimeTest. Helper functions: set. Direct tests: FuseLstatReturnMtimeTest.ReturnedFileMtimeIsCorrect; FuseLstatReturnMtimeTest.ReturnedDirMtimeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnMtimeTest.ReturnedFileMtimeIsCorrect; FuseLstatReturnMtimeTest.ReturnedDirMtimeIsCorrect. Assertion/mocking density: EXPECT_EQ x4.
