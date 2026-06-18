<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/028 -->
# sources/test-tools/xfstests/tests/ext4/028

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/028_research.md`.

Source read: 46 lines, SHA256 prefix `5281742b759a3368`.

Purpose: FS QA Test No. 028 Populate filesystem, check that fsmap -n10000 matches fsmap -n1. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/populate`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature_enabled "extent"`, `_require_populate_commands`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_scratch_ext4_feature_enabled "extent"; L34: _scratch_populate_cached nofill > $seqres.full 2>&1; L37: _scratch_mount; L38: $XFS_IO_PROG -c 'fsmap -n 65536' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/a; L39: $XFS_IO_PROG -c 'fsmap -n 1' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/b; L42: diff -uw $TEST_DIR/a $TEST_DIR/b.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data; visible subtest labels include Format and mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/028 -->
