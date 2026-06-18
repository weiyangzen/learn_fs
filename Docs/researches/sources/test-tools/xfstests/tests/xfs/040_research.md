<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/040 -->
# sources/test-tools/xfstests/tests/xfs/040

## Purpose
xfsprogs maintainer comparison test for libxfs. It requires kernel and xfsprogs workareas and runs `tools/libxfs-diff` against the kernel libxfs tree with hunk headers normalized.

## Important APIs, Types, And Functions
`_begin_fstest other auto` declares xfstests groups/tags: other, auto. Imports `common/preamble`, `common/filter`. Local helpers: `filter_libxfs_diff()`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/040 -->
