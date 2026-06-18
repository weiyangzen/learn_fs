# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/FileSystemTest.cpp

Purpose: This file adapts the generic fspp filesystem test suite to CryFS by providing a `CryFsTestFixture` implementation backed by a real `CryDevice`.

Important APIs/types/functions: Includes: fspp/fstest/FsTest.h, cpp-utils/tempfile/TempFile.h, cpp-utils/io/NoninteractiveConsole.h, cryfs/impl/filesystem/CryDevice.h, cryfs/impl/config/CryConfigLoader.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, ../testutils/MockConsole.h, ../testutils/TestWithFakeHomeDirectory.h. Classes/fixtures: CryFsTestFixture. Helper functions: failOnIntegrityViolation, CryFsTestFixture, createDevice. Direct tests: none.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It creates temp basedir/config state, fake home local-state, and a CryFS device used by inherited generic filesystem tests.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Fixture wiring must match the generic fspp expectations; otherwise broad filesystem conformance coverage may give misleading failures.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: EXPECT_TRUE x1.
