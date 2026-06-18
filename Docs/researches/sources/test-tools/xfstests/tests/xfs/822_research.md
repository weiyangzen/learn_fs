<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/822 -->
# sources/test-tools/xfstests/tests/xfs/822

Purpose: races fsstress against realtime reverse-map btree scrub to detect crashes, livelocks, or rtrmapbt scrub races.

Important APIs, types, and functions: uses `_require_realtime`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature realtime/rmapbt`, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_scrub -s 'scrub rtrmapbt %rgno%'`.

Control flow: format scratch, mount, require realtime and rmapbt, force new files to realtime storage, and run scrub stress for each realtime group placeholder.

State and persistence behavior: scratch contents are mutated under fsstress while rtrmapbt scrub reads metadata.

Dependencies and integration points: integrates with realtime XFS geometry, xfs_io scrub command templates, and xfstests stress cleanup.

Risks and test signals: skips without realtime/rmapbt. Success is no kernel crash, no livelock, and `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/822 -->
