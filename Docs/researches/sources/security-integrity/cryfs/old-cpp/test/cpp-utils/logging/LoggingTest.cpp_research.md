# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingTest.cpp

Purpose: Tests the higher-level logging facade/macros, including emitted message content, level filtering, logger names, and captured output behavior.

Important APIs and types: Uses cpp-utils logging headers, `LoggingTest` helpers, GoogleTest, and captured output utilities.

Control flow: Tests configure logging, emit messages at different levels or through different loggers, and assert captured output matches expected content or suppression.

State and persistence behavior: Runtime logging configuration and sink/capture state are process-local. No persistent log file is central unless the production API writes one under test.

Dependencies and integration points: Logging is used across CLI and library diagnostics, so facade behavior affects observability and tests that capture stderr/stdout.

Risks: Global logging state can leak across tests. Formatting expectations can become brittle when timestamps or prefixes change.

Test signals: Expected log text, level filtering, logger selection, and clean restoration of logging state.
