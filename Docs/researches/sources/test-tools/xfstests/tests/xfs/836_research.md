<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/836 -->
# sources/test-tools/xfstests/tests/xfs/836

Purpose: stress-tests online repair of realtime reference count btrees while fsstress mutates a realtime reflink filesystem.

Important APIs, types, and functions: requires realtime, scratch, `_require_xfs_stress_online_repair`, realtime and reflink feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_online_repair -s 'repair rtrefcountbt %rgno%'`.

Control flow: the test formats and mounts scratch, verifies realtime and reflink features, forces realtime allocation, and runs the online repair stress template.

State and persistence behavior: state is transient scratch filesystem metadata plus online repair activity, with cleanup stopping stress workers.

Dependencies and integration points: integrates with realtime refcountbt online repair and xfstests fsstress_online_repair.

Risks and test signals: target failures are kernel crashes, repair races, and livelocks. Expected output is `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/836 -->
