<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245

## Purpose
This fixture exercises syzkaller's Linux report parser on a long x86 stack-unwinder warning where the canonical title must be `WARNING: kernel stack regs has bad value`. The source is a 897-line console log dominated by raw `unwind stack type` frame dumps and ending with both `kernel stack regs ... bad 'bp' value` and `kernel stack frame pointer ... bad value` warnings.

## Important APIs, Types, and Functions
The file is data consumed by `ParseTest` in `pkg/report/report_test.go`, using only the `TITLE` header followed by raw log text. Parser APIs under test include `Reporter.Parse`, Linux oops matching, `findFirstOops`, title formatting, and the Linux suppression list. Kernel symbols that act as parser context include `__save_stack_trace`, `keccakf`, `save_trace`, `mark_lock`, `__lock_acquire`, `lock_sock_nested`, `__sys_bind`, `__x64_sys_sendto`, and syscall-return frames.

## Control Flow
The test harness reads the `TITLE` header, treats the remainder as the log, and asks the Linux reporter to find the first report signature. The reporter must ignore hundreds of pointer-value stack dump lines and choose the explicit warning near the end, without requiring a normal call trace because the matching oops rule is marked as a no-stack-trace report.

## State and Persistence Behavior
There is no mutable state. The persistent contract is the checked-in expected title and the specific raw log shape with sanitized `(ptrval)` tokens, repeated addresses, and two equivalent stack-register warnings.

## Dependencies and Integration Points
This fixture depends on the Linux oops table entries for `WARNING: kernel stack regs .* bad 'bp' value` and `WARNING: kernel stack frame pointer .* bad value`, plus generic printk prefix stripping and corruption detection. It integrates through `TestParse` and the Linux reporter selected for the test target.

## Risks and Edge Cases
The main risk is false extraction from the huge preceding stack dump, where many function-like tokens look like useful frames. Another risk is title drift if the parser starts preferring the later frame-pointer variant or demands stack traces for this warning family.

## Test Signals
A passing parse yields title `WARNING: kernel stack regs has bad value`, no explicit crash type, no panic/corruption flags, and a report beginning at the actual warning rather than at earlier `unwind stack type` data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245 -->
