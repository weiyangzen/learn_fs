# File Research: sources/virtualization/spdk/app/spdk_lspci/Makefile

## Purpose
Builds `spdk_lspci`, a small utility for listing PCI devices visible through SPDK's NVMe/VMD PCI drivers.

## Main Contents
- Sets `APP = spdk_lspci`.
- Compiles `spdk_lspci.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make rules and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, and common app build infrastructure.

## Filesystem/Block Relevance
Helps discover NVMe PCI devices usable by SPDK block/NVMe applications.

## Risks and Notes
- It is a standalone env utility, not an SPDK event app.
