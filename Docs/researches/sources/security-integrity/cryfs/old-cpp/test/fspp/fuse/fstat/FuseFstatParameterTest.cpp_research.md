# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatParameterTest.cpp

Purpose: This file tests fspp FUSE file-descriptor stat handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFstatTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFstatParameterTest. Helper functions: CallFstat. Direct tests: FuseFstatParameterTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFstatParameterTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
