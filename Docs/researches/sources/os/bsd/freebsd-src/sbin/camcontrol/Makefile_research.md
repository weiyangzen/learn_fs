# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/Makefile

## Purpose
Builds `camcontrol`, the CAM storage control utility.

## Main Elements
- Builds many command modules: `camcontrol.c`, `attrib.c`, `depop.c`, `epc.c`, `fwdownload.c`, `modeedit.c`, `persist.c`, `progress.c`, `timestamp.c`, `util.c`, and `zone.c`.
- Pulls NVMe helper sources from `sbin/nvmecontrol` and `sys/dev/nvme`.
- Adds include paths for NVMe control and `libnvmf`.
- Lowers warnings to 3 on ARM due to a noted build issue.
- Links `cam`, `nvmf`, `sbuf`, and `util`.
- Installs `camcontrol.8`.

## Dependencies And Integration
Combines SCSI, ATA, NVMe, and NVMf support under one utility.

## Risk Notes
This makefile includes sources from outside the local directory, so API drift in `nvmecontrol` helpers can affect `camcontrol`.
