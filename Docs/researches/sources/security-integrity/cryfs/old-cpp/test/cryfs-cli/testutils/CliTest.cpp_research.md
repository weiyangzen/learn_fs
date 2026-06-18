# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.cpp

Purpose: This translation unit includes `CliTest.h` so the CLI test fixture header is compiled as part of the test target. It does not add behavior beyond forcing compile/link validation for the header-only fixture methods.

Important APIs/types/functions: The only dependency is `CliTest.h`; all fixture APIs are defined inline in that header.

Control flow: Build flow includes this file in the test executable, which compiles the fixture definitions and catches missing includes or incompatible inline code.

State and persistence behavior: No runtime state is created here.

Dependencies and integration points: It connects the CLI fixture header to the CMake source list and Google Test executable.

Risks: Because behavior lives in the header, test coverage depends on downstream test files actually using the fixture.

Test signals: Successful compilation is the main signal from this file.
