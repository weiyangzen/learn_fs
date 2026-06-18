# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/iscsiboot_prop.c

## Role

`iscsiboot_prop.c` contains common helpers for iSCSI boot properties: optional diagnostic printing, freeing boot-property subfields, IP address formatting, and construction of iSCSI boot paths.

## Boot Property Printing

`iscsi_print_boot_property()` prints the global `iscsiboot_prop` when `iscsi_print_bootprop` is enabled. It delegates to initiator, NIC, and target printers.

The printed data includes initiator name, initiator CHAP name, local IP/gateway/DHCP/MAC, target name/IP/port/LUN, and target CHAP name. CHAP secrets are freed by the cleanup routines but not printed here.

`kinet_ntoa()` formats IPv4 as dotted decimal and IPv6 as colon-separated 16-bit hex groups without compression.

## Memory Cleanup

`iscsi_boot_free_ini()` frees initiator name, CHAP name, and CHAP secret buffers and clears pointers/lengths.

`iscsi_boot_free_tgt()` frees target name, CHAP name, CHAP secret, and boot parameter buffers and clears pointers/lengths.

`iscsi_boot_prop_free()` nulls the global pointer and frees nested initiator and target allocations from the saved structure.

## Boot Path Construction

`get_iscsi_bootpath_vhci()` builds a `/iscsi/ssd@...` boot path from target name, TPGT, LUN, and boot parameters. It lazily calls `ld_ib_prop()` when global boot properties are absent.

`get_iscsi_bootpath_phy()` builds a `/iscsi/disk@...` boot path, first passing the target name through `replace_sp_c()`.

`replace_sp_c()` percent-encodes special characters in target names: `:`, space, `@`, and `/`.

## Research Notes

This file is small but sits on the early-boot storage path. Hotspots are fixed-size path buffers, unchecked assumptions about target-name length during escaping, endian interpretation of the boot LUN bytes, and ensuring boot-property ownership is consistent with the partial free behavior.
