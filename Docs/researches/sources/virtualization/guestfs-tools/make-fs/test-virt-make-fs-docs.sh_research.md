# File Research: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs-docs.sh

## Role

Documentation coverage test for `virt-make-fs`.

## Behavior

The script runs `podcheck.pl "$srcdir/virt-make-fs.pod" virt-make-fs --ignore=--debug` after common setup and skip handling.

## Research Notes

`--debug` is accepted for compatibility with the old Perl tool and is intentionally ignored in documentation parity checks.
