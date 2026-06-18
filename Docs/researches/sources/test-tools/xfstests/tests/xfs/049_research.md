<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/049 -->
# sources/test-tools/xfstests/tests/xfs/049

## Purpose
`sources/test-tools/xfstests/tests/xfs/049` is a XFS functional regression test. XFS on loop test The `_begin_fstest` declaration is `_begin_fstest rw auto quick`, which places the test in the `rw, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_log`. Required capabilities: `_require_nonexternal`; `_require_scratch_nocheck`; `_require_no_large_scratch_dev`; `_require_loop`; `_require_extra_fs ext2`; `_require_non_zoned_device $SCRATCH_DEV`. External and harness commands observed in the full source include `mkfs`, `mount`, `umount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "--- mounts at end (after cleanup)" >> $seqres.full`; `echo "--- $*"`; `echo "--- $*" >> $seqres.full`; `echo "(dev=$SCRATCH_DEV, mount=$SCRATCH_MNT)" >> $seqres.full`; `echo "" >> $seqres.full`; `echo "--- mounts" >> $seqres.full`; `echo y | mkfs -t ext2 $loop_dev2 >> $seqres.full 2>&1 \`; `echo "--- mounts at end (before cleanup)" >> $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/049.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "--- mounts at end (after cleanup)" >> $seqres.full`, `echo "--- $*"`, `echo "--- $*" >> $seqres.full`. The script has 121 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/049 -->
