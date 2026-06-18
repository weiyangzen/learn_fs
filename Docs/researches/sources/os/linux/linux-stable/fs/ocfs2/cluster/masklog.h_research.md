# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.h

## Summary
Defines OCFS2/O2CB masked logging categories, bit operations, and logging macros.

## Main Responsibilities
- Define log categories for TCP, messages, heartbeat, DLM, quorum, cluster, errors, notices, and kthreads.
- Define initial masks and debug/non-debug compile-time allowed bits.
- Provide efficient 32-bit and 64-bit `u64` mask operations.
- Declare global allow/deny masks and the print backend.
- Provide `mlog()`, `mlog_ratelimited()`, `mlog_errno()`, and `mlog_bug_on_msg()` macros.
- Declare sysfs logmask lifecycle functions.

## Key Interfaces
- `mlog(mask, fmt, ...)` is the primary cluster logging macro.
- `mlog_errno()` suppresses common non-error control returns such as restart, interrupt, ENOSPC, and EDQUOT.
- `mlog_bug_on_msg()` logs context before `BUG()`.

## Risks
Compile-time filtering depends on `ML_ALLOWED_BITS`; non-error masks compile away unless `CONFIG_OCFS2_DEBUG_MASKLOG` is enabled. Developers adding new categories must update `masklog.c`.
