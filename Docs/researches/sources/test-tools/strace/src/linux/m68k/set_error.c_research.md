<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_error.c -->
# sources/test-tools/strace/src/linux/m68k/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `m68k` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc

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
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/set_error.c`: 20 lines; 344 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_error.c -->
