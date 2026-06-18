<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_scno.c -->
# sources/test-tools/strace/src/linux/m68k/set_scno.c

## Purpose
Implements syscall-number rewriting for `m68k` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/set_scno.c`: 15 lines; 324 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_scno.c -->
