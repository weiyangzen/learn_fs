# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.h

Purpose: This file provides the shared FUSE flush handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFlushTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for flush handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
