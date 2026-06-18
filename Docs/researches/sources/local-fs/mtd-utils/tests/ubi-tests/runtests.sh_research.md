# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/runtests.sh

## Role
Simple runner for the compiled UBI test suite.

## Main Behavior
- Requires one argument: a UBI device node.
- Verifies the argument is a character device.
- Runs `mkvol_basic mkvol_bad mkvol_paral rsvol io_basic io_read io_update io_paral volrefcnt` in order.
- Stops on first failure and prints `FAILURE`; prints `SUCCESS` if all pass.

## Interfaces And Dependencies
- Expects test binaries in the current directory.
- Uses POSIX shell with `set -euf`.

## Notes
- The script does not include `integ`; that is a separate integrity stress test.
