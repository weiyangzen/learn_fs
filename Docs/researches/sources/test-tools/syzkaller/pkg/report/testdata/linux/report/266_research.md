<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266

## Purpose
This shorter soft-lockup fixture covers the rmdir path without a panic flag. Expected title is `BUG: soft lockup in sys_rmdir`, with alternates for `__x64_sys_rmdir` and stall spellings, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, three `ALT` entries, and `TYPE`. Parser paths include soft-lockup matching, syscall normalization, alternate generation, and stack parsing. Key symbols include `d_walk`, `check_memory_region`, `_raw_spin_unlock`, `shrink_dcache_parent`, `vfs_rmdir`, `do_rmdir`, `__x64_sys_rmdir`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control Flow
The reporter reads one watchdog soft-lockup report and extracts the rmdir stack. Unlike report 264, there is no subsequent panic line, so the parser must leave `PANICKED` false while still classifying the hang.

## State and Persistence Behavior
The file is immutable test data with no runtime state. Persistent metadata is title, alternates, and HANG type.

## Dependencies and Integration Points
It depends on Linux soft-lockup regexes, syscall alias handling, and alternate-title sorting.

## Risks and Edge Cases
The top RIP is `check_memory_region`, not the intended syscall. Parser frame scoring must follow the stack to `__x64_sys_rmdir` and normalize it.

## Test Signals
Expected output is the rmdir soft-lockup title/alternates, type `HANG`, and no panic flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266 -->
