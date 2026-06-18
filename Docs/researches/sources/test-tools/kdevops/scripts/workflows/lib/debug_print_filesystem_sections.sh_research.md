# sources/test-tools/kdevops/scripts/workflows/lib/debug_print_filesystem_sections.sh

## Purpose
Debug helper that prints configured fstests filesystem sections for ext4, xfs, and btrfs.

## Important APIs and control flow
The script sets `TOPDIR=$PWD`, sources `scripts/workflows/fstests/ext4/lib.sh`, `btrfs/lib.sh`, and `xfs/lib.sh`, then echoes `EXT4_SECTIONS`, `XFS_SECTIONS`, and `BTRFS_SECTIONS`.

## State and dependencies
No persistent state. It depends on being run from the kdevops root and on the filesystem-specific helper libraries defining the section variables.

## Integration points
Located under `workflows/lib`, so it is shared support for filesystem workflow debugging and configuration inspection.

## Risks and test signals
It forcibly sets `TOPDIR` to the current directory, so running outside the repository root breaks the source paths. Test by invoking from the root and verifying non-empty section lists for enabled filesystem helpers.
