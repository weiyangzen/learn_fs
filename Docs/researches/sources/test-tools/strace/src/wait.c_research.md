<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/wait.c -->
# sources/test-tools/strace/src/wait.c

Purpose: Wait-family decoders for `waitpid`, `wait4`, and `waitid`; formats wait status bitfields, ptrace events, ids, options, siginfo, and rusage.

Important APIs/types/functions:
- SYS_FUNC handlers: `waitpid`, `wait4`, `osf_wait4`, `waitid`
- Helper functions include `print_wait_status`, `printwaitn`
- Direct includes: `"defs.h"`, `"ptrace.h"`, `"wait.h"`, `"xlat/wait4_options.h"`, `"xlat/ptrace_events.h"`, `"xlat/waitid_types.h"`
- Xlat tables consumed: `wait4_options`, `ptrace_events`, `waitid_types`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `P_PID`, `P_PIDFD`, `P_PGID`

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants
- integrates with ptrace tracee access

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/wait.c -->
