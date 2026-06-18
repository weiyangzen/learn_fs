# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkFilenameTest.cpp

Purpose: This file tests fspp FUSE unlink handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseUnlinkTest.h. Classes/fixtures: FuseUnlinkFilenameTest. Helper functions: none visible. Direct tests: FuseUnlinkFilenameTest.Unlink; FuseUnlinkFilenameTest.UnlinkNested; FuseUnlinkFilenameTest.UnlinkNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for unlink handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUnlinkFilenameTest.Unlink; FuseUnlinkFilenameTest.UnlinkNested; FuseUnlinkFilenameTest.UnlinkNested2. Assertion/mocking density: EXPECT_CALL x3.
