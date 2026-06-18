<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/835 -->
# sources/test-tools/xfstests/tests/xfs/835

Purpose: stress-tests scrub of realtime reference count btrees while fsstress mutates a realtime reflink filesystem.

Important APIs, types, and functions: requires realtime, scratch, `_require_xfs_stress_scrub`, realtime and reflink feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_scrub -s 'scrub rtrefcountbt %rgno%'`.

Control flow: mkfs, mount, verify realtime and reflink, force realtime allocation, then run scrub stress against the realtime refcount btree per realtime group.

State and persistence behavior: scratch realtime refcount metadata changes under fsstress and scrub observation.

Dependencies and integration points: depends on realtime reflink XFS and the scrub stress harness.

Risks and test signals: intended to catch crashes and livelocks. Success emits `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/835 -->
