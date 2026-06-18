# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/exit_status.cpp

Purpose: Helper executable for subprocess tests. It exits with requested status codes and emits predictable output so parent tests can validate capture and error handling.

Important APIs and types: Uses standard `iostream` and `cstdlib`; implements `main`.

Control flow: `main` reads command-line arguments, optionally prints output, and returns the requested code.

State and persistence behavior: No persistent state; only process exit status and stdout/stderr are observed.

Dependencies and integration points: Built as `cpp-utils-test_exit_status` and used by `SubprocessTest.cpp`.

Risks: Any change to output text or argument handling must be coordinated with subprocess assertions.

Test signals: Parent tests observe expected output and exit codes across success and failure cases.
