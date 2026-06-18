# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockConsole.h

Purpose: This header provides `MockConsole` and the `TestWithMockConsole` fixture mixin for tests that verify interactive CryFS prompts and console output.

Important APIs/types/functions: It uses Google Mock to mock console methods such as line input, password input, yes/no prompts, and output streams. The helper returns shared mock console instances for config and CLI tests.

Control flow: A test installs expectations on the mock console, invokes the target component, and then Google Mock verifies prompt order, prompt text, returned answers, and warnings.

State and persistence behavior: Console state is in-memory mock expectation state. It does not persist files, but it often controls whether production code creates or mutates config/local-state files.

Dependencies and integration points: This mock is central to `CryConfigConsole`, `CryConfigCreator`, `CryConfigLoader`, password key-provider, and filesystem tests that need deterministic interactive behavior.

Risks: Tests can become brittle if they assert exact prompt wording. Missing expectations can also hide unexpected console calls depending on mock strictness.

Test signals: Expected prompt calls, output calls, and absence/presence of warning messages are the main signals.
