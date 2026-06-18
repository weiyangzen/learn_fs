<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/064 -->
# sources/test-tools/xfstests/tests/xfs/064

## Purpose
`sources/test-tools/xfstests/tests/xfs/064` is a xfsdump/xfsrestore coverage test. test multilevel dump and restores with hardlinks The `_begin_fstest` declaration is `_begin_fstest dump auto`, which places the test in the `dump, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/dump`. Local helper surface: `_ls_size_filter`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfsrestore`, `mkfs`, `mount`, `quota`, `lstat64`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Do the incremental dumps"`; `echo "********* level $i ***********" >>$seqres.full`; `echo "Listing of what files we start with:"`; `echo "Look at what files are contained in the inc. dump"`; `echo ""`; `echo "restoring from df.level$i"`; `echo "Do the cumulative restores"`; `echo "ls -l restore_dir"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/064.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Do the incremental dumps"`, `echo "********* level $i ***********" >>$seqres.full`, `echo "Listing of what files we start with:"`. The script has 94 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/064 -->
