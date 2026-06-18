<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/824 -->
# sources/test-tools/xfstests/tests/xfs/824

Purpose: races fsstress against online repair of realtime reverse-map btrees.

Important APIs, types, and functions: uses `_require_realtime`, `_require_xfs_stress_online_repair`, realtime/rmapbt feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_online_repair -s 'repair rtrmapbt %rgno%'`.

Control flow: the script formats and mounts scratch, verifies realtime and rmapbt support, forces realtime allocation, and launches the online repair stress command template.

State and persistence behavior: all mutations occur in the scratch realtime volume and repair metadata state, removed by test cleanup.

Dependencies and integration points: integrates with xfs_io online repair command templates and the fsstress_online_repair harness.

Risks and test signals: skips without realtime/rmapbt or online repair support. Signals are no crash, no livelock, and `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/824 -->
