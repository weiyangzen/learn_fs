<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/008 -->
# sources/test-tools/xfstests/tests/xfs/008

## Purpose
Random-hole file layout test. It runs `src/randholes` with buffered and direct I/O parameters, counts holes with `xfs_bmap`, and accepts tolerance for random distribution and extent-size/realtime flags.

## Important APIs, Types, And Functions
`_begin_fstest rw ioctl auto quick` declares xfstests groups/tags: rw, ioctl, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_filter()`, `_do_test()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `$here/src/randholes`, `xfs_bmap`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `rm -f $tmp.*`; line 18: `rm -rf $TEST_DIR/randholes.$$.*`; line 30: `_do_test()`; line 61: `xfs_bmap -vvv $out >>$seqres.full`; line 77: `_do_test 1 50 "-l `expr 200 \* $blksize` -c 50 -b $blksize"`; line 78: `_do_test 2 100 "-l `expr 400 \* $blksize` -c 100 -b $blksize"`; line 79: `_do_test 3 100 "-l `expr 400 \* $blksize` -c 100 -b 512" # test partial blocks`; line 82: `_do_test 4 50 "-d -l `expr 200 \* $blksize` -c 50 -b $blksize"`; line 83: `_do_test 5 100 "-d -l `expr 400 \* $blksize` -c 100 -b $blksize"`.

## State And Persistence
State is kept in shell variables such as `blksize`, `_n`, `_holes`, `_param`, `out`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/008 -->
