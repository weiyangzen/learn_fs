<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001 -->
# sources/test-tools/xfstests/tests/ext4/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/001_research.md`.

Source read: 41 lines, SHA256 prefix `e0ee3c18b085f592`.

Purpose: FS QA Test No. 001 Test fallocate FALLOC_FL_ZERO_RANGE.

Important APIs/types/functions: test tags `auto prealloc quick zero fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fzero"`, `_require_test`; key variables `seqfull=$0`, `testfile=$TEST_DIR/001.$$`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L11: _begin_fstest auto prealloc quick zero fiemap; L20: _require_xfs_io_command "falloc"; L30: _test_generic_punch falloc fzero fzero fiemap _filter_fiemap $testfile; L33: _test_generic_punch -d falloc fzero fzero fiemap _filter_fiemap $testfile; L36: _test_generic_punch -k falloc fzero fzero fiemap _filter_fiemap $testfile; L39: _test_generic_punch -d -k falloc fzero fzero fiemap _filter_fiemap $testfile.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: fiemap extent layout and flags.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001 -->
