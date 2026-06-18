<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258

## Purpose
This compact fixture checks the BUG spelling of the lock-held-on-return report. The expected title is `BUG: lock held when returning to user space in fuse_lock_inode`.

## Important APIs, Types, and Functions
The file uses only a `TITLE` header. Parser coverage targets the Linux matcher for `[ BUG: lock held when returning to user space! ]`, the detail line `leaving the kernel with locks still held`, and the `at: fuse_lock_inode+0xa2/0xd0` frame. A distractor `somethingelse+0xa2/0xd0` appears after the real frame.

## Control Flow
The Linux reporter matches the BUG-form title, reads the subsequent details, extracts `fuse_lock_inode` from the `at:` line, and stops before the unrelated trailing symbol.

## State and Persistence Behavior
No state is owned. The persistent test data is the short raw log and expected title, with no explicit type or flags.

## Dependencies and Integration Points
It depends on the Linux BUG lock-held regex and function extraction rules in `pkg/report/linux.go`.

## Risks and Edge Cases
The nearby `somethingelse` line is a guard against choosing a later arbitrary symbol. The short input also tests no-stack report handling.

## Test Signals
A passing parse returns exactly `BUG: lock held when returning to user space in fuse_lock_inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258 -->
