<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/839 -->
# sources/test-tools/xfstests/tests/xfs/839

Purpose: checks that software atomic-write recovery completes correctly after an injected crash during a fragmented-file atomic write.

Important APIs, types, and functions: uses `punch-alternating`, `_scratch_inject_error free_extent`, `_simple_atomic_write`, `statx` atomic write queries, `cmp`, `md5sum`, and cycle mount recovery.

Control flow: create fragmented data and a check file, write expected post-atomic content to the check file, sync, inject `free_extent`, perform a direct atomic write that shuts down the filesystem, verify a later touch fails, remount for recovery, and compare final contents.

State and persistence behavior: scratch journal/recovery state is intentionally exercised across shutdown and remount.

Dependencies and integration points: depends on atomicwrites helpers, xfs_io error injection, punch-alternating helper, and multi-fsblock atomic write support.

Risks and test signals: skips if maximum atomic unit is too small. Failure signals include stray post-shutdown file creation or content mismatch after recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/839 -->
