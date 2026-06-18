# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/logging/Logger.h`.

Important APIs and types: Includes the logger public header.

Control flow: No runtime tests are defined.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects logging interface consumers from hidden include-order requirements.

Risks: Does not validate emitted log lines or logger state; behavior tests cover that separately.

Test signals: Successful compilation.
