<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/074 -->
# sources/test-tools/xfstests/tests/xfs/074

## Purpose
`sources/test-tools/xfstests/tests/xfs/074` is a XFS functional regression test. Check some extent size hint boundary conditions that can result in MAXEXTLEN overflows. In xfs_bmap_extsize_align(), we had, if ((temp = (align_alen % extsz))) { align_alen += extsz - temp; } align_alen had the value of 2097151 (i.e. MAXEXTLEN) blocks. extsz had the value of 4096 blocks. align_alen % extsz will be 4095. so align_alen will end up having 2097151 + (4096 - 4095) = 2097152 i.e. (MAXEXTLEN + 1). Thus the length of the new extent will be larger than MAXEXTLEN. This will later cause the bmbt leaf to have an entry whose length is set to zero block count. The `_begin_fstest` declaration is `_begin_fstest quick auto prealloc rw`, which places the test in the `quick, auto, prealloc, rw` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_command "falloc"`; `_require_loop`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "Silence is golden"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/074.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 84 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/074 -->
