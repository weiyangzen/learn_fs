<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/027 -->
# sources/test-tools/xfstests/tests/ext4/027

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/027_research.md`.

Source read: 56 lines, SHA256 prefix `9387b3e7bbd2242d`.

Purpose: FS QA Test No. 027 Check that getfsmap reports the BG metadata we're expecting. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L31: _scratch_mkfs > "$seqres.full" 2>&1; L32: _scratch_mount; L35: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT > $TEST_DIR/fsmap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/027 -->
