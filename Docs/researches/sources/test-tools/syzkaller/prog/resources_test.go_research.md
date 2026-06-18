## sources/test-tools/syzkaller/prog/resources_test.go

Purpose: validates resource constructor discovery, transitive syscall enablement, optional input handling, special linux resources, and generator resource creation.

Important APIs/types/functions: `TestResourceCtors`, `TestTransitivelyEnabledCalls`, `TestTransitivelyEnabledCallsLinux`, `TestTransitivelyEnabledAutoCalls`, `TestGetInputResources`, `TestClockGettime`, `TestCreateResourceRotation`, `TestCreateResourceHalf`, `testCreateResource`, and `TestPreferPreciseResources`.

Control flow: tests enumerate target resources and syscalls, remove selected constructors, compare disabled reasons, run resource creation for every input resource in enabled call sets, and count constructor preferences over repeated generation.

State and persistence: in-memory target metadata and generated calls only.

Dependencies/integration: integrates resource code with generated targets, rotator selection, choice tables, and random generation.

Risks: linux-specific counts are tied to current descriptions. Random preference checks use thresholds rather than exact distributions.

Test signals: strong coverage for dependency correctness, especially preventing generation of calls whose required resources cannot be produced.
