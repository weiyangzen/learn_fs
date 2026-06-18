# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/closeFile/FuseCloseTest.cpp

Purpose: This file tests fspp FUSE close-file handling, focusing on close-file forwarding from POSIX close to the fspp close method.

Important APIs/types/functions: Includes: ../../testutils/FuseTest.h, ../../testutils/OpenFileHandle.h, condition_variable. Classes/fixtures: Barrier, FuseCloseTest. Helper functions: Barrier, WaitAtMost, Release, OpenAndCloseFile, OpenFile, CloseFile. Direct tests: FuseCloseTest.CloseFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for close-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCloseTest.CloseFile. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x3.
