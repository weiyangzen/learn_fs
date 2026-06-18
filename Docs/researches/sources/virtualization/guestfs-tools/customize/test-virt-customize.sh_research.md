# File Research: sources/virtualization/guestfs-tools/customize/test-virt-customize.sh

## Scope

Basic runtime test for `virt-customize` using a qcow2 overlay of a phony Fedora guest.

## Behavior

- Requires the phony Fedora guest.
- Creates a qcow2 image backed by the raw Fedora fixture.
- Runs `virt-customize` to write `/etc/motd`, write `/etc/motd2`, write then delete `/etc/motd3`.
- Uses `guestfish` to verify motd contents and that `/etc/motd3` is absent.
- Removes generated files on success.

## Dependencies And Risks

- Covers write/delete customization operations on qcow2.
- Depends on qemu-img and guestfish.
