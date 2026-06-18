## sources/test-tools/xfstests/tests/btrfs/022

Purpose: this qgroup limit test verifies that a subvolume with a 5 MiB qgroup limit rejects a 10 MiB write.

Important local API: `_limit_test_exceed` creates subvolume `a`, enables quotas, finds its subvolume id, applies `qgroup limit 5M`, attempts to write 10 MiB with `_ddt`, and fails the test if the write succeeds.

Control flow: it requires scratch, qgroup rescan support, qgroup report support, and no compression, then formats/mounts scratch, runs the exceed test, unmounts, and checks scratch.

State and persistence: scratch contains subvolume `a`, quota metadata, and a partially written or rejected file. `units` is initialized from `_btrfs_qgroup_units` for consistency with reporting helpers.

Dependencies: `_require_qgroup_rescan`, `_require_btrfs_qgroup_report`, `_require_no_compress`, `_btrfs subvolume/quota/qgroup`, `_btrfs_get_subvolid`, `_ddt`, and `_check_scratch_fs`.

Risks: compression must be disabled because compressed data usage can avoid the intended limit. The test only checks that the write command returns nonzero, not the exact errno. qgroup enforcement timing must be synchronous enough for the dd failure.

Test signals: expected output is `Silence is golden`; if the oversized write succeeds, `_fail "quota should have limited us"` is emitted.
