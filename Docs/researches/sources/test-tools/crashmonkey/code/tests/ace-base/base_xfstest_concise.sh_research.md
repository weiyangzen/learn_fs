# sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest_concise.sh

Purpose: extended xfstests shell template with additional concise helpers for fallocate/fzero/fpunch/fsync consistency cases.

Important APIs/functions: includes all base xfstest helpers plus `ensure_file_size_one_block()`, `translate_range()`, `do_falloc()`, and `do_fsync_check()`. These map symbolic ranges/modes into `xfs_io` fallocate/fzero/fpunch commands and consistency checks.

Control flow: after standard scratch/flakey setup, helper definitions are loaded and the script currently exits successfully without generated test cases.

State and persistence behavior: intended generated tests would mutate files under `$SCRATCH_MNT`, use dm-flakey drop/remount, and compare data/metadata with `general_stat`.

Dependencies: xfstests framework, dm-flakey, `$XFS_IO_PROG`, stat/od/coreutils, and scratch-device variables.

Risks: `[[ size -lt 4192 ]]` omits `$` and likely tests a literal string, so `ensure_file_size_one_block()` is broken. Unquoted variables and `rm -rf $(find ...)` are whitespace-sensitive. `translate_range()` sets `length` to `offset + 32768` for append, which may be intended as a length but reads like an end offset.

Test signals: generated fallocate/fsync tests should produce no output on success and before/after detail on mismatch.
