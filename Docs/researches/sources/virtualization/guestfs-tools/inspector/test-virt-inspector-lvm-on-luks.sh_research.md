# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-lvm-on-luks.sh

## Role

Regression test for `virt-inspector` on a Fedora phony guest with LVM layered on LUKS.

## Behavior

After common test setup and skip handling, the script targets `fedora-lvm-on-luks.img`. If the image is non-empty, it pipes the `FEDORA` passphrase to `virt-inspector --keys-from-stdin --format=raw -a`, writes `actual-$b.xml`, validates the XML against the Relax NG schema, and diffs it against the expected XML with `$diff_ignore`.

## Research Notes

This validates stdin-based key handling for encrypted images and checks that inspector output remains deterministic.
