## sources/test-tools/xfstests/tests/btrfs/028

Purpose: this qgroup/balance stress test checks qgroup accounting while extents are dereferenced during relocation.

Control flow: it requires scratch and btrfs qgroup report support, formats and mounts scratch, enables quota, runs qgroup rescan, starts fsstress in the background with operations weighted toward writes, unlinks, creates, and fsyncs, starts `_btrfs_stress_balance` in the background, sleeps for `30 * TIME_FACTOR`, kills fsstress and balance, and relies on post-test btrfs check to validate qgroup accounting.

State and persistence: scratch contains a stress directory with rapidly changing files and quota metadata. `balance_pid` tracks the background balance process for cleanup.

Dependencies: `_scale_fsstress_args`, `_run_fsstress_bg`, `_kill_fsstress`, `_btrfs_stress_balance`, `_btrfs_kill_stress_balance_pid`, `_qgroup_rescan`, and `_require_btrfs_qgroup_report`.

Risks: timing-sensitive stress test; 30 seconds may be insufficient on some systems or excessive on slow ones. There is no direct qgroup output comparison; validation is deferred to btrfs check after unmount. Cleanup must kill both background workload and balance to avoid spillover.

Test signals: expected output is `Silence is golden`; qgroup accounting failures are expected to surface during btrfs check/fsck or as kernel warnings.
