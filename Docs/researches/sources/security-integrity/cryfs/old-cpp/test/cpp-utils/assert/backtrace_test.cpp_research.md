# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/backtrace_test.cpp

Purpose: Tests backtrace collection and crash/exception reporting across normal exceptions, null pointer access, signals, aborts, and unknown exit codes. It validates both direct backtrace content and subprocess crash diagnostics.

Important APIs and types: Uses `cpp-utils/assert/backtrace.h`, `cpp-utils/process/subprocess.h`, `my-gtest-main.h`, Boost filesystem, signal APIs, and platform-specific Windows branches.

Control flow: Helper functions run the `exit_signal` helper executable with different modes or signals, capture output/status, and assert that reports include stack frames, signal names, or exception messages. Direct tests also ensure caught exceptions do not crash backtrace handling.

State and persistence behavior: Runtime state is subprocess exit status and captured output. No durable files are expected beyond helper binary execution.

Dependencies and integration points: Integrates assertion backtrace code, signal handling, subprocess execution, and test-main crash hooks.

Risks: Highly platform-sensitive: signals, symbolization, line numbers, and Windows exception handling differ by OS/compiler. Tests can be flaky if stack traces are stripped.

Test signals: Expected signal names, exception text, backtrace markers, non-crashing caught-exception path, and correct subprocess failures.
