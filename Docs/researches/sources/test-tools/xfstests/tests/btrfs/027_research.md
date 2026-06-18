## sources/test-tools/xfstests/tests/btrfs/027

Purpose: this replace/raid regression test verifies replacing a missing btrfs device across supported profile configurations.

Important local API: `run_test mkfs_opts` reserves one spare device, formats the remaining pool with the requested profile, writes data files, wipes the second device to simulate loss, remounts degraded, replaces the missing device id with the spare using `replace start -B -f -r`, scrubs, unmounts, checks the filesystem, and releases pool state.

Control flow: it requires scratch without automatic check, five equal-sized pool devices, profile configs for `replace-missing`, and `wipefs`, then loops over `_btrfs_profile_configs`.

State and persistence: each loop destroys and recreates scratch pool filesystems. One pool member is wiped to simulate a missing device; the spare becomes part of the filesystem if replace succeeds.

Dependencies: `_btrfs_get_profile_configs`, device-pool helpers, `$WIPEFS_PROG`, `$BTRFS_UTIL_PROG filesystem show/replace/scrub`, `_ddt`, `_check_scratch_fs`, and degraded btrfs mount support.

Risks: destructive to all pool devices. The missing device is selected as the second device and its btrfs device id is parsed from `filesystem show`, which is format-sensitive. Failed cases return from the loop after cleanup rather than failing globally, so coverage can be conditional.

Test signals: stdout starts with `Silence is golden`; full-log entries identify each profile. Replace, scrub, and fs check must succeed for effective coverage.
