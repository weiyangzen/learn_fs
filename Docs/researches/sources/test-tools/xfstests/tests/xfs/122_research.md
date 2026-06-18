<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/122 -->
# sources/test-tools/xfstests/tests/xfs/122

## Purpose
`sources/test-tools/xfstests/tests/xfs/122` is a realtime geometry/allocation regression test. pv#952498 Keep an eye on some of the xfs type sizes Motivation from differing ondisk types for 32 and 64 bit word versions. The `_begin_fstest` declaration is `_begin_fstest other auto quick clone realtime`, which places the test in the `other, auto, quick, clone, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: `_type_size_filter`, `_type_name_filter`, `_attribute_filter`. Required capabilities: `_require_command "$INDENT_PROG" indent`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `xfs_growfs`, `mkfs`, `mount`, `bstat`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "#include <$(echo "$hdr" | sed -e 's|/usr/include/||g')>" >> $cprog`; `echo 'int main(int argc, char *argv[]) {' >>$cprog`; `echo 'return 0; }' >>$cprog`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/122.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "#include <$(echo "$hdr" | sed -e 's|/usr/include/||g')>" >> $cprog`, `echo 'int main(int argc, char *argv[]) {' >>$cprog`, `echo 'return 0; }' >>$cprog`. The script has 239 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/122 -->
