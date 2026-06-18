# File Research: sources/os/bsd/freebsd-src/sbin/newfs/runtest01.sh

Regression script checking deterministic image creation. It creates two 1 MB malloc-backed md devices, labels both, runs `./newfs -R` on both, and compares the resulting raw partitions.

Key behaviors:
- Uses md units `99` and `98`.
- Passes if `cmp /dev/md99c /dev/md98c` succeeds.
- Cleans up both md devices before and after.
- Returns shell exit code based on comparison result.

Research notes:
- This specifically exercises the deterministic timestamp/random path in `mkfs.c`.
