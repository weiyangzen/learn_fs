<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/816 -->
# sources/test-tools/xfstests/tests/xfs/816

Purpose: races fsstress against online metapath repair operations to validate metadata-directory path repair under concurrent filesystem activity.

Important APIs, types, and functions: probes `xfs_io -x -c 'repair metapath ...'`, filters benign `did not need repair` output, builds repair commands for quota, realtime directory, and realtime group metadata paths, then calls `_scratch_xfs_stress_online_repair`.

Control flow: the script formats and mounts scratch, discovers all supported repair metapath verbs, logs the verb list, converts each into a `repair metapath` stress command, and runs the online repair stress harness.

State and persistence behavior: state is transient scratch filesystem activity and repair attempts. Cleanup stops stress scrub/repair background jobs.

Dependencies and integration points: depends on online repair support, xfs_io metapath commands, realtime group count from mkfs output, and xfstests stress helpers.

Risks and test signals: no discovered verbs causes `_notrun`. Signals are no crash, no livelock, and quiet completion with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/816 -->
