# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingLevelTest.cpp

Purpose: Tests logging-level parsing, ordering, formatting, or filtering behavior. It protects the contract for severity levels used by the logging facade.

Important APIs and types: Uses logging level types/functions from cpp-utils and GoogleTest/GoogleMock.

Control flow: Test cases compare levels, convert between enum/string forms, and validate which messages should be emitted or suppressed for configured levels.

State and persistence behavior: Process-local logging configuration may be changed during tests. No durable persistence is expected.

Dependencies and integration points: Logging levels influence CLI verbosity, diagnostics, and test log capture throughout CryFS.

Risks: Global logging state must be reset between tests. String names are user-facing and compatibility-sensitive.

Test signals: Exact level conversions, ordering comparisons, and enabled/disabled message behavior.
