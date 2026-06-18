<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c -->
# sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c

## Purpose
Fetches MicroBlaze result registers before syscall-exit decoding.

## Important APIs, Types, and Functions
- `get_syscall_result_regs(struct tcb *tcp)` reads `PT_GPR(3)` into the static `microblaze_r3` cache with `upeek`.

## Control Flow
- On syscall exit, the helper peeks the result register and returns the ptrace read status.

## State and Persistence Behavior
- Updates only the local cached result register used by `get_error.c`.

## Dependencies and Integration Points
- Called by the generic syscall-result path before MicroBlaze error decoding.

## Risks and Edge Cases
- If the peek fails or uses the wrong offset, later success/error decoding reads stale or invalid data.

## Test Signals
- Trace success and failure syscalls while checking that `microblaze_r3`-based return decoding matches kernel results.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c`: 12 lines; 243 bytes; functions `get_syscall_result_regs`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c -->
