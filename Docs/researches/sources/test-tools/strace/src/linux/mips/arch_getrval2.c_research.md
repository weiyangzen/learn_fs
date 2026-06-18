<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/mips/arch_getrval2.c

## Purpose
Returns the architecture-specific second syscall return value for `mips` when the ABI exposes one.

## Important APIs, Types, and Functions
- `getrval2(struct tcb *tcp)` refreshes registers if ptrace syscall-info requires it and returns the second result register (`gr[9]` on IA-64 or `uregs[3]`/`v1` on MIPS).

## Control Flow
- Fetch registers if necessary, then return the ABI second-result register as a `long`.

## State and Persistence Behavior
- No persistence; it reads the current cached register snapshot.

## Dependencies and Integration Points
- Used when syscall decoders request `RVAL2` handling through `HAVE_ARCH_GETRVAL2`.

## Risks and Edge Cases
- Register freshness and ABI selection matter; a stale snapshot returns the previous syscall's secondary value.

## Test Signals
- Trace syscalls with two return values, especially `pipe` on ABIs that report file descriptors in two registers.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_getrval2.c`: 14 lines; 265 bytes; functions `getrval2`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_getrval2.c -->
