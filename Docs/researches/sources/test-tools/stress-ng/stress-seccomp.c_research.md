# sources/test-tools/stress-ng/stress-seccomp.c

Purpose: implements `seccomp`, an OS security stressor that repeatedly forks children, installs seccomp BPF filters, and verifies allowed versus trapped syscalls.

Important APIs/types/functions: `stress_seccomp_info` provides a `supported` probe and `VERIFY_ALWAYS`. Static BPF programs include allow-all, allow-open/write/close/exit, allow-open/close/exit without write, and randomized filter storage. `stress_seccomp_supported()` forks a probe child to test `SECCOMP_SET_MODE_FILTER`. `stress_seccomp_set_huge_filter()` explores filter-size limits. `stress_seccomp_set_filter()` sets `PR_SET_NO_NEW_PRIVS`, exercises seccomp query operations, invalid ops, strict mode probes, `seccomp()` and `prctl(PR_SET_SECCOMP)` fallback. `stress_sigsys()` exits with `EXIT_TRAPPED`.

Control flow: `stress_seccomp()` synchronizes and loops. Each iteration randomly decides whether write should be allowed and whether to try a random filter, then forks. The child disables dumpability, installs a SIGSYS handler, tries a huge allow filter, installs the selected filter, opens `/dev/null`, writes `TEST\n`, closes, and exits. The parent waits and verifies that disallowed write exits through the SIGSYS path while allowed write does not die from SIGSYS.

State and persistence: state is static filter arrays and per-child seccomp state. Seccomp filters are process-local and die with the child. No filesystem changes occur beyond opening `/dev/null`.

Dependencies and integration points: requires Linux audit/filter/seccomp/prctl headers, `PR_SET_SECCOMP`, and `SECCOMP_SET_MODE_FILTER`. It integrates with shim seccomp, waitpid, process dumpability, signal helpers, random helpers, and bogo counters.

Risks and test signals: seccomp may require capabilities or be disabled; random BPF filters are retried with safe filters on install failure. Critical signals are support-skip correctness, expected `EXIT_TRAPPED` for blocked writes, no unexpected child failures, and bogo increments after each verified child.
