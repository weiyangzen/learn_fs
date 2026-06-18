# File Research: sources/os/bsd/freebsd-src/sbin/bectl/tests/bectl_test.sh

## Purpose
ATF shell test suite for `bectl`, exercising real ZFS pools backed by sparse disk images.

## Main Elements
- Setup helpers:
  - Generates a temporary zpool name.
  - Creates sparse disk image, zpool, `ROOT`, and default BE datasets.
  - Creates deep BE layouts with child `/usr` dataset.
  - Destroys the zpool during cleanup.
- Test cases:
  - `bectl_create`: standard, snapshot, snapshot-derived, recursive, empty BE, and invalid option combinations.
  - `bectl_destroy`: destroy behavior, origin handling, clone chains, snapshot destruction with clones.
  - `bectl_export_import`: BE stream export/import and post-destroy checks.
  - `bectl_list`: verifies created/destroyed BEs appear and disappear.
  - `bectl_mount`: both `unmount` and `umount` aliases.
  - `bectl_rename`: dataset rename visibility.
  - `bectl_jail`: batch and command jails, numeric BE names, explicit jid/name/path, `ujail`/`unjail`, and cleanup behavior.
  - `bectl_promotion`: activation promotes clone chains out of clone status.
  - `bectl_destroy_bootonce`: destroying a bootonce BE clears `zfsbootcfg`.
  - `bectl_rename_bootonce`: renaming a bootonce BE updates `zfsbootcfg`.
- Skips known CI/problem architectures `i386` and `armv7` for referenced PRs.
- Requires root, ZFS module, sparse-file support, and for jail tests `/rescue/rescue`.

## Dependencies And Integration
Uses ATF, `zpool`, `zfs`, `bectl`, `zfsbootcfg`, `jail`, `jls`, sparse files, and root privileges.

## Risk Notes
Tests create and destroy zpools with generated names. Cleanup is defensive, especially for jails left behind after failures.
