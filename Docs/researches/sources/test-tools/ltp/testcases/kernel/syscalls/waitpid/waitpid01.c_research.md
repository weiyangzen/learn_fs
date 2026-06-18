<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c

Purpose: verifies `waitpid()` reports signal-terminated children correctly for a broad set of standard signals and for both `raise(sig)` and `kill(getpid(), sig)` child paths.

Important APIs/types/functions: `testcase_list[]` maps signals to expected core-dump behavior; `variant_list[]` selects child trigger function. `setup()` adjusts `RLIMIT_CORE` to allow minimal core dumps when possible. `run()` resets signal disposition, forks, waits with `waitpid(pid, &status, 0)`, and checks `WIFSIGNALED`, `WTERMSIG`, and optionally `WCOREDUMP`.

Control flow/state: each signal/variant pair is independent. Child terminates by signal; parent inspects the status word. Temporary directory support exists for core files.

Dependencies/integration: LTP variants multiply coverage across trigger mechanisms. Core-dump checks are conditional on rlimit capacity.

Risks/test signals: signal defaults and platform core-dump policy affect `WCOREDUMP`; the primary contract is pid and terminating signal. `SIGKILL` cannot have its handler reset and is handled specially.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid01.c -->
