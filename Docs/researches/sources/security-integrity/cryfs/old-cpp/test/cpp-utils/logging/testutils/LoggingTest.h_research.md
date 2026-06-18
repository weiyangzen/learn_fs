# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/testutils/LoggingTest.h

Purpose: Declares shared utilities for logging tests, centralizing setup, capture, and assertions around global logging behavior.

Important APIs and types: Provides a `LoggingTest` fixture/helper around logger setup and expected output checks. It integrates with GoogleTest and cpp-utils logging classes.

Control flow: Downstream tests use the fixture to configure logging state, emit messages, and restore state after assertions.

State and persistence behavior: Manages process-global logging sinks/levels during test scope. No durable persistence is required.

Dependencies and integration points: Supports `LoggerTest`, `LoggingLevelTest`, and `LoggingTest` suites by preventing duplicated global setup.

Risks: Any missed teardown can contaminate later tests. Helpers must avoid hiding important behavior such as exact output destinations.

Test signals: Tests using the helper should see isolated logging state and deterministic captured output.
