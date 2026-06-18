<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h

Purpose: Shared probe for `syncfs()` availability; it calls the wrapper once and converts missing syscall support into an LTP configuration skip.

Important APIs/types/functions: defines `check_syncfs`; touches `syncfs`; uses constants/macros such as `EINVAL`, `TCONF`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is dirty data tied to a specific mounted filesystem and file descriptor; only that filesystem should be flushed by `syncfs()`.

Dependencies and integration points: Depends on `check_syncfs.h`, raw syscall wrappers, mounted test devices, block write counters, and per-filesystem descriptor setup. Direct includes: none beyond consumers.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/check_syncfs.h -->
