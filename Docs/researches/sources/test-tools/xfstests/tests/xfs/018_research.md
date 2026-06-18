<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/018 -->
# sources/test-tools/xfstests/tests/xfs/018

## Purpose
Log attribute replay (LARP) test. It enables `/sys/fs/xfs/debug/larp`, uses error injection during xattr set/remove operations across internal, leaf, node, remote, zero-length, and transition cases, remounts to replay the log, and verifies recovered attribute contents by checksum.

## Important APIs, Types, And Functions
`_begin_fstest auto quick attr` declares xfstests groups/tags: auto, quick, attr. Imports `common/preamble`, `common/filter`, `common/attr`, `common/inject`. Local helpers: `_cleanup()`, `test_attr_replay()`, `create_test_file()`, `require_larp()`. Feature gates/fix annotations include `_require_scratch`, `_require_scratch_xfs_crc`, `_require_attrs`, `_require_xfs_io_error_injection`, `_require_xfs_sysfs`. External helper programs used include `$ATTR_PROG`.

## Control Flow
The test is a XFS extended-attribute/log-replay test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -rf $tmp.*`; line 34: `_scratch_inject_error $error_tag`; line 50: `touch $testfile 2>&1 | _filter_scratch`; line 53: `_scratch_remount_dump_log >> $seqres.full`; line 56: `touch $testfile`; line 59: `$ATTR_PROG -l $testfile >> $seqres.full`; line 62: `$ATTR_PROG -q -g $attr_name $testfile 2> /dev/null | md5sum;`; line 73: `touch $filename`; line 77: `$ATTR_PROG -s "attr_name$i" -V $attr_value $filename >> \`; line 84: `touch $SCRATCH_MNT/a`.

## State And Persistence
State is kept in shell variables such as `testfile`, `attr_name`, `attr_value`, `flag`, `error_tag`, `filename`, `count`, `ORIG_XFS_LARP`, `attr16`, `attr17`, `attr64`, `attr256`, and 11 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/018 -->
