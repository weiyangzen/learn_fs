# File Research: sources/teaching/minix/minix/drivers/storage/mmc/omap_mmc.h

## Purpose

Defines OMAP MMCHS controller structures, register-offset tables, and bit masks used by the MINIX MMC host drivers.

## API Surface

- `struct omap_mmchs`: virtual/physical base, size, IRQ, and register-layout pointer.
- `struct omap_mmchs_registers`: named offsets for SYSCONFIG, SYSSTATUS, CON, BLK, ARG, CMD, response registers, DATA, PSTATE, HCTL, SYSCTL, interrupt registers, and capability registers.
- `regs_v1`: AM335x register layout.
- `regs_v0`: DM37xx register layout shifted by 0x100.
- Macros define reset, idle, power, bus width, clock, command, present-state, timeout, interrupt, and capability bit fields.

## Dependencies

Consumed by `emmc.c` and `mmchost_mmchs.c` together with MINIX MMIO helpers.

## Risks

The register tables are static objects. `emmc.c` mutates `regs_v1` into absolute virtual addresses, while `mmchost_mmchs.c` treats offsets as offsets under `io_base`; mixing those usage patterns in one process would be unsafe. Bit-mask correctness is hardware-critical, and one typo in command or interrupt bits can break all card I/O.
