<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.h -->
# sources/test-tools/strace/tests/k_sockopt.h

Purpose: Shared header for kernel socket option tests.

Important APIs/types/functions: Declares the shared testing interface and constants consumed by `k_sockopt.c` without pulling in unrelated test logic.

Control flow: Header-only file; there is no runtime control flow. It is included by the C test at compile time.

State/persistence behavior: No runtime state. Any state is in constants/macros compiled into including tests.

Dependencies: Coupled to the strace test framework and raw socket option syscall tests.

Integration points: Keeps declarations in one place for raw kernel socket option coverage.

Risks: Prototype drift between header and C file would cause build failures or wrong syscall argument types.

Test signals: Successful compilation of `k_sockopt.c` is the primary signal.

Source read signal: complete file read for this research pass; file size 24 line(s), 684 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.h -->
