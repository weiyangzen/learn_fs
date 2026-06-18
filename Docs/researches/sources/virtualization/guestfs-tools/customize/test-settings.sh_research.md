# File Research: sources/virtualization/guestfs-tools/customize/test-settings.sh

## Scope

Slow integration test for virt-builder hostname, timezone, and firstboot settings.

## Behavior

- Requires slow-test mode, one guest name argument, x86_64 host, qemu, and a known public template.
- Builds a guest with hostname `test-set.example.com`, timezone `Japan`, and a generated firstboot script.
- Firstboot script records hostname, FQDN, timezone offset where supported, syncs, and powers off.
- Boots the guest under qemu.
- Uses `guestfish` to download `/firstboot.out` and print debug files.
- Verifies observed hostname/FQDN/timezone fields when present.
- Cleans disk and firstboot artifacts.

## Dependencies And Risks

- Guest-family conditionals handle differences in hostname/FQDN/timezone support.
- Requires firstboot to run to completion inside the guest.
- Public template behavior can change over time.
