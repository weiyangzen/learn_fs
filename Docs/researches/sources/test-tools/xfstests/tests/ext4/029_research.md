<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/029 -->
# sources/test-tools/xfstests/tests/ext4/029

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/029_research.md`.

Source read: 46 lines, SHA256 prefix `9758db059032daa9`.

Purpose: FS QA Test No. 029 Check that getfsmap reports external log devices Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_logdev`, `_require_scratch`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`; key variables `data_dev=$(grep 'static fs metadata' $TEST_DIR/fsmap | head -n 1 | awk '{print $2}')`, `journal_dev=$(grep 'journalling log' $TEST_DIR/fsmap | head -n 1 | awk '{print $2}')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L32: _scratch_mkfs > "$seqres.full" 2>&1; L33: _scratch_mount; L36: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT >> $seqres.full; L37: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT | tr '[]()' ' ' > $TEST_DIR/fsmap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and mount; Check device field of FS metadata and journalling log.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/029 -->
