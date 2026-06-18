## sources/test-tools/xfstests/tests/btrfs/014

Purpose: this balance stress test runs repeated snapshot create/delete operations concurrently with repeated balance operations.

Important local APIs: `_create_snapshot` loops 20 times creating and deleting `snapshot0`. `_balance` loops 20 times running `_run_btrfs_balance_start`.

Control flow: it requires scratch, formats and mounts it, prints a dmesg hint, starts `_create_snapshot` in the background, starts `_balance` in the background, and waits for both.

State and persistence: scratch is repeatedly modified by temporary snapshots and balance relocation. `$seqres.full` receives balance logs.

Dependencies: `$BTRFS_UTIL_PROG`, `_run_btrfs_balance_start`, `_scratch_mkfs`, `_scratch_mount`, and shell job control.

Risks: no explicit content verification is performed; the test is intended to expose crashes, warnings, or command failures. Both background functions operate on the same scratch root, so races are intentional. Snapshot command failures are not wrapped in `_fail`.

Test signals: exit success plus absence of dmesg errors is the primary signal. The printed hint tells humans to inspect dmesg on failure.
