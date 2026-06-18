# File Research: sources/local-fs/ocfs2-tools/tests/mkfs-test.sh

## Purpose
Destructive mkfs regression test driver for `mkfs.ocfs2`, followed by fsck and metadata verification.

## Main Behavior
- Creates timestamped logs and counts pass/fail tests.
- Tests combinations of block size and cluster size:
  - block sizes: `512 1024 2048 4096`
  - cluster sizes: `4096` through `1048576`
  - formats with `mkfs.ocfs2 -x -M local -L mkfstest -b ... -C ...`
  - verifies with `fsck.ocfs2 -fy` and `tunefs.ocfs2 -Q "B=%B;C=%T;"`
- Tests journal sizes `4M`, `64M`, `128M`, `256M`, verifying journal inode size with `debugfs.ocfs2`.
- Tests node slot counts `2 8 16 32 64 128 255`, verifying with `tunefs.ocfs2 -Q "N=%N;"`.
- Tests fstype profiles `mail`, `datafiles`, and `vmstore`.
- Tests short and maximum-length volume labels, verifying with `tunefs.ocfs2 -Q "V=%V;"`.
- Tests UUID input in compact and hyphenated forms.

## Dependencies
- Root privileges via `sudo`.
- A real block device supplied with `-d`; script refuses non-block devices.
- `mkfs.ocfs2`, `fsck.ocfs2`, `tunefs.ocfs2`, `debugfs.ocfs2`, `awk`, shell utilities.

## Safety Notes
This script repeatedly formats the target block device. It is destructive by design.
