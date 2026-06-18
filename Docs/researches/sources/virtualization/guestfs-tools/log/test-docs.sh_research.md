# File Research: sources/virtualization/guestfs-tools/log/test-docs.sh

## Role

Documentation coverage test for `virt-log`.

## Behavior

The script uses the common test harness, strict/trace shell mode, skip handling, and runs `podcheck.pl "$srcdir/virt-log.pod" virt-log --path $top_srcdir/common/options`.

## Research Notes

It verifies option parity among the binary, help output, and POD documentation.
