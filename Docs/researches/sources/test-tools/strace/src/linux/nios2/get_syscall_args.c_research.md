<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/nios2/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `nios2` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- arguments come from regs[4] through regs[9]
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `nios2`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/get_syscall_args.c`: 19 lines; 471 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_syscall_args.c -->
