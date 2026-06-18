# File Research: sources/local-fs/ocfs2-tools/tests/fsck-test.sh

## Purpose
Destructive test driver for `fsck.ocfs2`, using `fswreck` to corrupt a block device and verifying whether `fsck.ocfs2 -fy` repairs it.

## Main Behavior
- Locates tools through `PATH`, `/sbin`, `which`, and wraps commands in `sudo -u root`.
- Creates a timestamped log directory.
- Iterates fswreck corruption codes from `STARTCODE` to `ENDCODE`, defaulting to `0..500`.
- For each valid code:
  - Uses `fswreck -C <code> -M` to obtain mkfs corruption options.
  - Runs `mkfs.ocfs2 -x <opts> -L fswreck <device>`.
  - Runs `fswreck -C <code> <device>`.
  - Runs `fsck.ocfs2 -fy <device>` if corruption succeeded.
  - Logs pass/fail and per-code output.
- Stops when `fswreck -L <code>` fails, treating that as no more valid corruption codes.

## Dependencies
- Root privileges via `sudo`.
- A real block device supplied with `-d`; script refuses non-block devices.
- `mkfs.ocfs2`, `fsck.ocfs2`, `fswreck`, `chown`, `date`, `mkdir`, `seq`.

## Safety Notes
This script formats and corrupts the specified block device. It is not safe for mounted or valuable data devices.
