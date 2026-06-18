# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-luks-on-lvm.sh

## Role

Regression test for `virt-inspector` on a Fedora phony guest with LUKS volumes layered on LVM.

## Behavior

The test requires libguestfs minor version at least 47 and skips empty image files. It defines three key selector sets: direct `/dev/Volume-Group/...` paths, escaped `/dev/mapper/...` paths, and repeated `all:key:` selectors.

For `fedora-luks-on-lvm.img`, it obtains the root LUKS UUID with `guestfish`, runs `virt-inspector` with raw format and explicit keys, validates the output against `virt-inspector.rng`, substitutes `ROOTUUID` into the expected XML, and diffs. It reruns with mapper-style keys and all-selector keys, diffing each output against the first actual XML.

## Research Notes

This is focused on encrypted-device selector compatibility and stable XML output once decryption succeeds.
