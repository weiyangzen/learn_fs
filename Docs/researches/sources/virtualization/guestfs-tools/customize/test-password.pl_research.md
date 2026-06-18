# File Research: sources/virtualization/guestfs-tools/customize/test-password.pl

## Scope

Slow Perl/Expect integration test for virt-builder root password customization.

## Behavior

- Requires `SLOW=1`, Perl `Expect`, one guest name argument, x86_64 host, qemu, and a known public virt-builder template.
- Unsets `VIRT_BUILDER_DIRS` to use public templates.
- Applies serial-console fixes for selected Debian/Ubuntu guests.
- Generates a random root password.
- Builds a guest with `virt-builder --root-password password:<password>`.
- Boots it in qemu with serial stdio, waits for login prompt, logs in as root, runs `ls -1 /`, and expects `home` in output.
- Removes disk and log on success.

## Dependencies And Risks

- Highly environment-dependent: public templates, qemu, host architecture, boot timing, and Expect availability.
- Password/login behavior is tested through actual guest boot, not static image inspection.
