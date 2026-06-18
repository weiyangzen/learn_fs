# File Research: sources/teaching/minix/minix/drivers/storage/mmc/sdhcreg.h

## Purpose

Provides NetBSD/OpenBSD-derived SD Host Controller standard register offsets, bit definitions, and helper macros.

## API Surface

Defines SDHC register offsets for DMA address, block size/count, argument, transfer mode, command, response, data, present state, host/power/clock control, software reset, interrupt status/enables, capabilities, and host version. It also defines bit masks for command responses, data direction, card presence, buffer readiness, errors, voltages, DMA, high speed support, and diagnostic bit strings.

## Dependencies

Included by MMCHS host code as a reference/compatibility header for SDHC-style constants.

## Risks

This header is declarative. Risks are primarily semantic drift if hardware-specific code assumes these standard SDHC offsets apply directly to OMAP MMCHS registers. The OMAP driver mostly uses `omap_mmc.h` for actual register offsets.
