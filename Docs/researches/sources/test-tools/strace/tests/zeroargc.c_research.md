# sources/test-tools/strace/tests/zeroargc.c

Purpose: small strace test helper that executes a target program with `argc == 0`, allowing execve/argv edge-case tracing.

Important APIs and control flow: `main` requires at least one operand, treats `av[1]` as the executable path, overwrites `av[1]` with NULL, then calls `execve(path, av + 1, av + 2)`. On failure it reports through `perror_msg_and_fail`.

State and persistence: mutates only its inherited argument vector and then replaces the process image; no durable state.

Dependencies and integration: includes `tests.h` for harness diagnostics and standard `execve`. It is used by tests that need a real process image launched with an empty argv vector and controlled environment tail.

Risks and test signals: platform kernels/libcs may vary in tolerance for zero-argc exec. A successful test signal is that the target image sees no argv entries; failure output must preserve the target path for diagnosis.
