# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-windows.sh

## Scope

Runtime output regression test for `virt-drivers` on the phony Windows guest.

## Behavior

- Requires the Windows phony guest.
- Runs `virt-drivers --format=raw -a windows.img` into XML.
- Strips optional `vendorname` and `devicename` attributes because hwdata may vary by environment.
- Diffs normalized output against `expected-windows.xml`, ignoring generated-by lines.
- Removes temporary XML files.

## Dependencies And Risks

- Tests stable driver detection while allowing environment-dependent hwdata enrichment.
