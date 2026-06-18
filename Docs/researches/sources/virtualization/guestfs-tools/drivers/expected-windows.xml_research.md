# File Research: sources/virtualization/guestfs-tools/drivers/expected-windows.xml

## Scope

Expected XML output fixture for `virt-drivers` on the phony Windows guest.

## Contents

- Describes one BIOS firmware Windows operating system rooted at `/dev/sda2`.
- Includes i386 arch, Windows distro/product metadata, client variant, version 6.1, and osinfo `win7`.
- Lists detected drivers:
  - `machine` with PCI vendor `8086` device `0008`.
  - `mshdc` with PCI class `000101`.

## Risks And Invariants

- Test strips optional `vendorname` and `devicename` attributes before comparison because hwdata availability varies.
- Generated-by version comment is ignored during diff.
