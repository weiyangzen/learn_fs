<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/003 -->
# sources/test-tools/xfstests/tests/ext4/003

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/003_research.md`.

Source read: 42 lines, SHA256 prefix `6137112860cd0958`.

Purpose: FS QA Test No. ext4/003 Regression test for commit: b5b6077 ext4: fix wrong assert in ext4_mb_normalize_request() This testcase checks whether this bug has been fixed. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature "bigalloc"`; helper functions `_cleanup()`; key variables `BLOCK_SIZE=$(_get_page_size)`, `features=bigalloc`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L17: _scratch_unmount; L27: _require_scratch_ext4_feature "bigalloc"; L36: _scratch_mount; L38: $XFS_IO_PROG -f -c "pwrite 0 256m -b 1M" $SCRATCH_MNT/testfile 2>&1 | \.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, ext-family mkfs/tune utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/003 -->
