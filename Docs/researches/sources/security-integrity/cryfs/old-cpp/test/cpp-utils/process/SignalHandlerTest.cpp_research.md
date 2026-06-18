# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalHandlerTest.cpp

Purpose: Tests lower-level signal handler registration for SIGINT and SIGTERM, including no-handler death, single-handler catch, wrong-signal death, combined handlers, and multiple handlers for one signal.

Important APIs and types: Uses `cpp-utils/process/SignalHandler.h`, GoogleTest death tests, and helper callbacks.

Control flow: Tests register handlers in scope, raise signals, and assert callback invocation or process death. Multiple-handler tests verify the active handler selection.

State and persistence behavior: Temporarily modifies global process signal handlers. No durable persistence.

Dependencies and integration points: `SignalCatcher` and CLI shutdown flows depend on this lower-level signal handling contract.

Risks: Global signal state can leak if RAII restoration fails. Death-test behavior varies by platform and test runner.

Test signals: Correct callback for configured signals, death for unhandled signals, and expected behavior with multiple handlers.
