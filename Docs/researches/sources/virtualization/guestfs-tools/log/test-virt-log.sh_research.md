# File Research: sources/virtualization/guestfs-tools/log/test-virt-log.sh

## Role

Functional smoke test for `virt-log` on phony guest images.

## Behavior

The script defines `can_handle`, which requires journal availability for `fedora.img` and allows other images. It creates a temporary output file, loops over Fedora, Debian, and Ubuntu phony images, skips empty or unsupported images, runs `$VG virt-log --format=raw -a "$f"` capturing stdout/stderr, prints the captured log output, and removes the temporary file.

## Research Notes

This is a smoke test rather than a golden diff test. It exercises log extraction paths while tolerating fixture/environment variation.
