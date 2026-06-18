# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalCatcherTest.cpp

Purpose: Tests scoped signal-catching behavior for SIGINT and SIGTERM. It verifies absence of a catcher causes death, active catchers intercept configured signals, multiple/nested catchers route signals correctly, and expired catchers restore previous behavior.

Important APIs and types: Uses `cpp-utils/process/SignalCatcher.h`, GoogleTest death tests, and `<csignal>`.

Control flow: Helper `raise_signal` triggers signals under different catcher scopes. Tests assert death or caught state depending on active catcher stack and signal order.

State and persistence behavior: Mutates process signal handlers during test scope and restores them through RAII. No persistent state.

Dependencies and integration points: Supports graceful CLI/process shutdown logic that reacts to interrupt/termination signals.

Risks: Signal tests are platform- and test-runner-sensitive. Global signal handlers require careful restoration to avoid contaminating later tests.

Test signals: Expected death without catcher, correct catcher notified for each signal, nested handler precedence, and restored default behavior after scope exit.
