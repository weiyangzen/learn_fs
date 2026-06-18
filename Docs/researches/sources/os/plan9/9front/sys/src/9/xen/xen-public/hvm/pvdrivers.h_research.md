# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/pvdrivers.h

Imported Xen public PV driver product registry.

Purpose:
- Defines a macro list of product IDs for HVM paravirtual driver packages.

Key content:
- Provides `PVDRIVERS_PRODUCT_LIST(EACH)` entries for xensource-windows, gplpv-windows, linux, and experimental.

Integration:
- HVM/PV-driver identification ABI; not directly used by 9front’s PV guest drivers.

Risks/notes:
- Registry values should not be invented locally; comments note product IDs should be allocated through Xen development process.
