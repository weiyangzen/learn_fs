<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/140 -->
# sources/test-tools/xfstests/tests/xfs/140

## Purpose
`sources/test-tools/xfstests/tests/xfs/140` is a reflink/refcount stress test. Try to ENOSPC while expanding the refcntbt by CoWing every other block of a file that eats the whole AG. The `_begin_fstest` declaration is `_begin_fstest auto clone`, which places the test in the `auto, clone` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_no_large_scratch_dev`; `_require_scratch_reflink`; `_require_cp_reflink`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create the original files"`; `echo "Compare files"`; `echo "CoW every other block"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/140.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`. The script has 72 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/140 -->
