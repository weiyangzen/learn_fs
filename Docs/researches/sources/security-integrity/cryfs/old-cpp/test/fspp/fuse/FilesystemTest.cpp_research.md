# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/FilesystemTest.cpp

Purpose: This file tests fspp FUSE `Filesystem` adapter wiring at a broader level than single-operation tests. It verifies context propagation and operation forwarding between mounted POSIX calls and the mocked filesystem implementation.

Important APIs/types/functions: Includes: fspp/fuse/Filesystem.h. Classes/fixtures: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: Tests mount a `MockFilesystem`, perform filesystem calls through the mount directory, and assert the adapter invokes the expected mock methods with correct context and parameters.

State and persistence behavior: Runtime state is the temporary mount, FUSE thread, context captured from the request, and mock expectation state. No persistent files should remain outside temp dirs.

Dependencies and integration points: This is the integration layer between POSIX/FUSE calls and the fspp `Filesystem` interface.

Risks: Context forwarding and method dispatch bugs can make operation-specific tests pass in isolation while real mounted behavior is wrong.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
