# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector.sh

## Role

Main regression test for `virt-inspector` phony guest images.

## Behavior

The script defines a `diff_ignore` pattern to ignore Windows NTFS UUID differences because ntfs-3g cannot always set them deterministically. It loops over Debian, Fedora, Ubuntu, Arch Linux, CoreOS, and Windows phony images. For each non-empty image, it runs `virt-inspector --format=raw -a`, validates output with `xmllint --relaxng virt-inspector.rng`, and diffs against the corresponding expected XML.

A commented mdadm two-disk Fedora test is present but disabled because mdadm support is problematic for many users.

## Research Notes

This test is the broadest golden-output guard for inspector XML across Linux and Windows guests.
