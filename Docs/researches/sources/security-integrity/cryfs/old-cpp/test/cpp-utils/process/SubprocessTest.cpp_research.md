# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SubprocessTest.cpp

Purpose: Tests subprocess invocation helpers for checked and unchecked calls, output capture, exit code handling, arguments containing spaces, command lookup through PATH, and calls from threads.

Important APIs and types: Uses `cpp-utils/process/subprocess.h`, Boost filesystem, `ConditionBarrier`, `LoopThread`, and `my-gtest-main` helpers. It depends on the `cpp-utils-test_exit_status` helper executable.

Control flow: Tests call helper commands that exit with success or specific errors, capture stdout/stderr, assert thrown exceptions for checked failures, inspect returned status/output for unchecked calls, and exercise threaded invocation.

State and persistence behavior: Runtime state is child process execution, captured output, exit status, environment/PATH lookup, and synchronization primitives. No intended persistent files.

Dependencies and integration points: Backtrace tests and CLI tests depend on reliable subprocess behavior.

Risks: PATH resolution, quoting, spaces in arguments, and threaded calls are platform-sensitive. Helper binary availability is coupled to CMake dependencies.

Test signals: Exact exit codes, output strings, expected exceptions, successful threaded execution, and correct handling of spaced arguments.
