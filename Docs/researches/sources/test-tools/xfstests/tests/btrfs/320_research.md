<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/320 -->
# sources/test-tools/xfstests/tests/btrfs/320

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/320_research.md`.

Source read: 105 lines, SHA256 prefix `3a3aa6d4f6fbbfbc`.

Purpose: FS QA Test No. 320 Test qgroups to validate the creation works, the counters are sane, rescan works, and we do not get failures when we write less than the limit amount..

Important APIs/types/functions: test tags `auto qgroup limit`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_qgroup_rescan`, `_require_btrfs_qgroup_report`, `_require_scratch_qgroup`; helper functions `_basic_test()`, `_rescan_test()`, `_limit_test_noexceed()`; key variables `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a)`, `a_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `a_shared=$(echo $a_shared | $AWK_PROG '{ print $2 }')`, `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT b)`, `b_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `b_shared=$(echo $b_shared | $AWK_PROG '{ print $2 }')`, `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a)`, `output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `refer=$(echo $output | $AWK_PROG '{ print $2 }')`, `excl=$(echo $output | $AWK_PROG '{ print $3 }')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_basic_test()`, `_rescan_test()`, `_limit_test_noexceed()`. Representative operation sequence: L17: _require_btrfs_qgroup_report; L18: _require_scratch_qgroup; L24: _btrfs subvolume create $SCRATCH_MNT/a; L25: _btrfs quota enable $SCRATCH_MNT/a; L27: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a); L28: $BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep $subvolid >> \; L31: _run_fsstress -d $SCRATCH_MNT/a -w -p 1 -n 2000; L32: _btrfs subvolume snapshot $SCRATCH_MNT/a \; L37: a_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L40: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT b); L42: b_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L44: $BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT >> $seqres.full; L54: _btrfs subvolume create $SCRATCH_MNT/a; L55: _btrfs quota enable $SCRATCH_MNT/a; L56: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a); L57: _run_fsstress -d $SCRATCH_MNT/a -w -p 1 -n 2000; L59: output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L64: output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid").

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/320 -->
