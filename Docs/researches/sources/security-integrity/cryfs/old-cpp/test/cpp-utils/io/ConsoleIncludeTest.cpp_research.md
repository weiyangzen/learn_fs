# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/io/Console.h`.

Important APIs and types: Includes the public console abstraction header.

Control flow: No runtime tests; compilation validates public include dependencies.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects users of the console interface, which is implemented by `IOStreamConsole` and tested in console behavior suites.

Risks: Compile-only coverage does not validate prompt or IO behavior.

Test signals: Successful compilation with direct public header inclusion.
