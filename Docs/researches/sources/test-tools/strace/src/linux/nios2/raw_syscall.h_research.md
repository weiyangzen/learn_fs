<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/raw_syscall.h -->
# sources/test-tools/strace/src/linux/nios2/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `nios2`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- trap with r2 carrying the syscall number/result and r7 carrying the error flag
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `nios2` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/raw_syscall.h`: 29 lines; 609 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/raw_syscall.h -->
