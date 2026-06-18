# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.cpp

Purpose: This source includes `CryTestBase.h` to compile the filesystem test fixture into the `cryfs-test` target. The fixture implementation is inline in the header, so this file mainly anchors the header in the build.

Important APIs/types/functions: The only visible dependency is `CryTestBase.h`.

Control flow: Build control flow compiles the header-defined fixture through this translation unit.

State and persistence behavior: No additional runtime state is introduced here.

Dependencies and integration points: It connects the CryFS filesystem fixture to the CMake test executable.

Risks: Behavioral regressions are caught through tests that inherit `CryTestBase`, not directly through this source.

Test signals: Successful compilation plus downstream fixture use are the signals.
