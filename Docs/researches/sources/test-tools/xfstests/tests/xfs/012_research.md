<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/012 -->
# sources/test-tools/xfstests/tests/xfs/012

## Purpose
Deterministic hole creation test using `src/holes`. It creates dense, sparse, and no-hole file patterns, counts holes with `xfs_bmap`, and dumps diagnostics on mismatch.

## Important APIs, Types, And Functions
`_begin_fstest rw auto quick` declares xfstests groups/tags: rw, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_filesize()`, `_do_test()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `$AWK_PROG`, `$here/src/holes`, `xfs_bmap`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `rm -f $tmp.*`; line 19: `rm -rf $TEST_DIR/holes.$$.*`; line 30: `_do_test()`; line 75: `xfs_bmap -vvv $out >>$seqres.full`; line 87: `_do_test 1 "-l 40960000 -b 40960 -i 10 -c 1" 100`; line 90: `_do_test 2 "-l 409600000 -b 40960 -i 1000 -c 1" 10`; line 93: `_do_test 3 "-l 40960000 -b 40960 -i 10 -c 10" 0`.

## State And Persistence
State is kept in shell variables such as `_n`, `_param`, `_count`, `failed`, `out`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/012 -->
