<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/823 -->
# sources/test-tools/xfstests/tests/xfs/823

Purpose: races fsstress against realtime bitmap online repair and covers command syntax differences across rtgroups and older scrub implementations.

Important APIs, types, and functions: uses `_scratch_xfs_stress_online_repair`, `_xfs_has_feature rtgroups`, `xfs_io -c 'help scrub'`, and repair templates `repair rtbitmap %rgno%`, `repair rtbitmap 0`, or `repair rtbitmap`.

Control flow: format/mount scratch, require realtime, force realtime allocation, choose the appropriate repair command form, then run online repair stress.

State and persistence behavior: scratch realtime bitmap state changes under fsstress and online repair. Cleanup stops background work.

Dependencies and integration points: depends on realtime XFS, online repair, xfs_io scrub help output, and xfstests xfs/inject/fuzzy helpers.

Risks and test signals: version-dependent command syntax is a key risk. Success is quiet stress completion without crash or livelock.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/823 -->
