<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/332 -->
# sources/test-tools/xfstests/tests/btrfs/332

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/332_research.md`.

Source read: 66 lines, SHA256 prefix `7c5b8522659e7734`.

Purpose: FS QA Test No. btrfs/332 Test tune enabling and removing squotas on a live filesystem Import common functions. real QA test starts here.

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_scratch_enable_simple_quota`, `_require_no_compress`, `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_fssum`, `_require_btrfs_dump_super`, `_require_btrfs_command inspect-internal dump-tree`; key variables `d1=$SCRATCH_MNT/d1`, `d2=$SCRATCH_MNT/d2`, `fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _require_scratch_enable_simple_quota; L18: _require_command "$BTRFS_TUNE_PROG" btrfstune; L20: _require_btrfs_dump_super; L21: _require_btrfs_command inspect-internal dump-tree; L22: $BTRFS_TUNE_PROG --help 2>&1 | grep -wq -- '--enable-simple-quota' || \; L23: _notrun "$BTRFS_TUNE_PROG too old (must support --enable-simple-quota)"; L24: $BTRFS_TUNE_PROG --help 2>&1 | grep -wq -- '--remove-simple-quota' || \; L25: _notrun "$BTRFS_TUNE_PROG too old (must support --remove-simple-quota)"; L27: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L28: _scratch_mount; L35: _run_fsstress -d $d1 -w -n 2000; L36: fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT); L39: _scratch_unmount; L40: $BTRFS_TUNE_PROG --enable-simple-quota $SCRATCH_DEV >> $seqres.full; L41: _check_btrfs_filesystem $SCRATCH_DEV; L42: _scratch_mount; L43: fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT); L48: _run_fsstress -d $d2 -w -n 2000.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/332 -->
