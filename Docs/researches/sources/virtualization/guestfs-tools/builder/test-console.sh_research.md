# File Research: sources/virtualization/guestfs-tools/builder/test-console.sh

## Scope

Slow integration test checking that virt-builder templates boot with a functional serial console.

## Behavior

- Intended to be invoked through generated `test-console-GUEST.sh` wrappers.
- Requires slow-test mode, a known virt-builder guest, x86_64 host, and `qemu-system-x86_64`.
- Unsets `VIRT_BUILDER_DIRS` to use public templates.
- Applies guest-specific fixes for Debian/Ubuntu serial console setup.
- Builds a guest disk with `virt-builder`, boots it under qemu with `-serial stdio`, sleeps 180 seconds, then kills qemu.
- Checks captured serial output for GRUB, kernel/systemd, login banner, and login prompt patterns depending on distro family.
- Removes generated disk and output on success.

## Dependencies And Risks

- Requires qemu/KVM or TCG fallback and public template availability.
- Fixed sleep/kill timing can be sensitive to host speed.
- Pattern expectations are distro-specific and may need updates as templates change.
