# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/exit_signal.cpp

Purpose: Helper executable used by backtrace tests to intentionally terminate through signals, access violations, aborts, and unhandled exceptions.

Important APIs and types: Includes `cpp-utils/assert/backtrace.h`, `<csignal>`, `<stdexcept>`, and Windows exception support where applicable. Implements `main` and signal/exception trigger helpers.

Control flow: `main` parses an argument or mode, installs backtrace handling where needed, then deliberately exits via the requested mechanism. The parent test process captures the result.

State and persistence behavior: No persistent state. It intentionally mutates process control flow by raising signals or throwing uncaught exceptions.

Dependencies and integration points: Built as `cpp-utils-test_exit_signal` and used by `backtrace_test.cpp` through subprocess utilities.

Risks: Behavior depends on OS signal semantics and compiler/runtime exception reporting. The helper must remain simple because any unrelated failure becomes a confusing backtrace-test failure.

Test signals: Parent tests observe expected nonzero exit status and diagnostic text for each termination mode.
