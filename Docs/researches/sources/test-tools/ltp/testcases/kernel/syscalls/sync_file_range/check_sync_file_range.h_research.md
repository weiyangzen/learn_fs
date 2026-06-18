<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h

Purpose: Shared probe for `sync_file_range()` availability; it calls the wrapper once and converts `ENOSYS` into an LTP configuration skip.

Important APIs/types/functions: defines `check_sync_file_range`; touches `sync_file_range`; uses constants/macros such as `EINVAL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct includes: none beyond consumers.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/check_sync_file_range.h -->
