<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/036 -->
# sources/test-tools/xfstests/tests/ext4/036

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/036_research.md`.

Source read: 41 lines, SHA256 prefix `9e59dd851e40bb6f`.

Purpose: FS QA Test No. ext4/036 Test truncate orphan inodes when mounting ext4 ext4 used to hit WARNING, this commit fixed the issue 721e3eb ext4: lock i_mutex when truncating orphan inodes Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`; key variables `testfile=$SCRATCH_MNT/testfile`, `inode=`ls -i $testfile | awk '{print $1}'``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _scratch_mkfs_sized $((16*1024*1024)) >>$seqres.full 2>&1; L25: _scratch_mount; L33: _scratch_unmount; L34: debugfs -w -R "set_super_value last_orphan $inode" $SCRATCH_DEV \; L38: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/036 -->
