<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/041 -->
# sources/test-tools/xfstests/tests/ext4/041

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/041_research.md`.

Source read: 52 lines, SHA256 prefix `e3ea2245c25168f9`.

Purpose: FSQA Test No. ext4/041 (was shared/007) Since loff_t is a signed type, it is invalid for a filesystem to load an inode with i_size = -1ULL. Unfortunately, nobody checks this, which means that we can trivially DoS the VFS by creating such a file and appending to it. This causes an integer overflow in the routines underlying writeback, which results in the kernel locking up. So, create this malformed inode and try a dio append to make sure we catch this situation..

Important APIs/types/functions: test tags `dangerous_fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch_nocheck`, `_require_command "$DEBUGFS_PROG"`; key variables `PIDS=""`, `testdir=$SCRATCH_MNT`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _require_scratch_nocheck; L26: _require_command "$DEBUGFS_PROG"; L29: _scratch_mkfs >> $seqres.full 2>&1; L30: _scratch_mount; L36: _scratch_unmount; L39: $DEBUGFS_PROG -w -R "sif /a size 0xFFFFFFFFFFFFFE00" $SCRATCH_DEV >> $seqres.full 2>&1; L42: $DEBUGFS_PROG -R "stat /a" $SCRATCH_DEV 2>&1 | grep -q "Size: 18446744073709551104" || \; L46: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Format and mount; Corrupt filesystem; Remount, try to append.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/041 -->
