<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257

## Purpose
This compact fixture checks the warning spelling for returning to user space while a lock is held. The expected title is `WARNING: lock held when returning to user space in fuse_lock_inode` and type `LOCKDEP`.

## Important APIs, Types, and Functions
Headers include `TITLE` and `TYPE`. Parser coverage targets the Linux regex for `WARNING: lock held when returning to user space`, its `leaving the kernel with locks still held` detail, and function extraction from `at: fuse_lock_inode+0xaf/0xe0`.

## Control Flow
The reporter sees the warning line, process context, the explanatory lock-held line, and the `at:` location. It does not need a full call trace; the oops-specific matcher extracts `fuse_lock_inode` directly.

## State and Persistence Behavior
The fixture stores a 10-line raw warning and expected lockdep classification. It has no runtime state.

## Dependencies and Integration Points
It depends on the Linux lock-held warning rule in `linux.go` and the generic report test harness.

## Risks and Edge Cases
The report is intentionally short; requiring a full stack would mark it corrupted. The title must retain the `WARNING:` prefix and not be rewritten to the `BUG:` variant.

## Test Signals
Expected output is title `WARNING: lock held when returning to user space in fuse_lock_inode` and type `LOCKDEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257 -->
