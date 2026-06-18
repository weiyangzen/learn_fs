<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/828 -->
# sources/test-tools/xfstests/tests/xfs/828

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrefcountbt` and the repair mode argument is `offline`. It narrows record fuzzing with `addr u${inode_ver}.rtrefcbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/828 -->
