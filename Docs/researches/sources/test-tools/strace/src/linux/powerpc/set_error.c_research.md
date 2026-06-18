<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_error.c -->
# sources/test-tools/strace/src/linux/powerpc/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `powerpc` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/set_error.c`: 27 lines; 536 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_error.c -->
