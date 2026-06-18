# File Research: sources/virtualization/guestfs-tools/cat/test-virt-cat.sh

## Scope

Runtime test for `virt-cat` against a phony Fedora guest.

## Behavior

- Reads `/etc/test1` from `fedora.img` and expects `abcdefg`.
- Reads `/etc/test2` and expects an empty string.
- Fails with diagnostics on mismatches.

## Dependencies And Risks

- Requires the phony Fedora image and exact fixture contents.
- Covers raw image mode and auto-inspection.
