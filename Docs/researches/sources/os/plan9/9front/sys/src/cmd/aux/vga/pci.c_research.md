# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.c

Small Plan 9 PCI enumeration and config-space access layer used by VGA controller modules.

Key behavior:
- Maintains global linked list `pcilist`/`pcitail` of `Pcidev` objects discovered from Plan 9 PCI device files.
- `pcicfginit` opens `/dev/pci` or fallback `#$/pci`, scans directory entries whose names contain `ctl`, parses bus/device/function from file names, opens each raw config file, reads the control file, parses class/vendor/device/interrupt and BAR/size records, reads revision ID from config space, and appends the device to the list.
- `pcicfgrw` performs little-endian pread/pwrite config-space transactions of length 1, 2, or 4 through the `rawfd`.
- Exports `pcicfgr8/16/32`, `pcicfgw8/16/32`, and `pcimatch`.
- `pcimatch` lazily initializes the device list and then returns the next matching vendor/device entry after `prev`, treating DID `0` as wildcard.

Notable dependencies:
- Plan 9 `/dev/pci` or `#$/pci` device file interface.
- Endian helpers `GBIT8/16/32` and `PBIT8/16/32`.
- `Pcidev` structure and constants from `pci.h`.

Research notes:
- Allocated `Dir *d` from `dirreadall` is not freed in this file; for a short-lived VGA setup utility this is low impact.
- Parsing assumes current Plan 9 PCI ctl formatting and fixed offsets into the read buffer for class/vendor/device fields.
- `strstr(d[i].name, "ctl")` is broad but works for the expected PCI control-file naming scheme.
