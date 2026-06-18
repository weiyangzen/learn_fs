<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_scno.c -->
# sources/test-tools/strace/src/linux/m68k/get_scno.c

## Purpose
Extracts the current `m68k` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `m68k` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/get_scno.c`: 14 lines; 275 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_scno.c -->
