# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/BasicFuseTest.cpp

Purpose: This file verifies basic FUSE mount/test-harness behavior for the fspp adapter, ensuring a temporary FUSE filesystem can be mounted and interacted with through the shared `FuseTest` infrastructure.

Important APIs/types/functions: Includes: ../testutils/FuseTest.h. Classes/fixtures: none visible. Direct tests: BasicFuseTest.setupAndTearDown.

Control flow: The test creates a temporary mounted filesystem backed by `MockFilesystem`, performs simple operations through the mount point, and relies on the FUSE thread fixture for startup/shutdown.

State and persistence behavior: State includes a temporary mount directory, FUSE thread lifecycle, and mock filesystem expectations. No durable state should survive teardown.

Dependencies and integration points: It validates the common harness used by every fspp FUSE operation test.

Risks: FUSE availability, mount timing, and teardown behavior are environmental risks that can affect the whole suite.

Test signals: Primary signals are BasicFuseTest.setupAndTearDown. Assertion/mocking density: none visible.
