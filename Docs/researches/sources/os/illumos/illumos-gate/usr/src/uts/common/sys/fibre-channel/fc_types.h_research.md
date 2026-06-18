# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_types.h

## Purpose

`fc_types.h` defines common Fibre Channel transport types, sysevent names, reset/DMA behavior enums, and kernel-only FC transport include aggregation.

## Main Types

`fc_hba_state_change_t` is a 64-bit state-change tracker.

`fc_portid_t` is an endian-dependent 24-bit FC port identifier plus private loop LILP position.

`fc_hardaddr_t` is an endian-dependent 24-bit hard address.

`fc_porttype_t` stores an FC port type byte.

`fc_reset_action_t` specifies how an FCA should return commands after reset: none, all, or only outstanding commands.

`fc_dma_behavior_t` controls streaming DMA behavior for unaligned buffers.

`fc_fcp_dma_t` selects whether FCP command/response allocation should use DVMA space.

`fc_ulp_rscn_info_t` carries ULP RSCN count information; zero is the invalid count sentinel.

## Interfaces and Includes

Sysevent class/subclass strings cover FC port attach/detach/online/offline/RSCN and target/device add/remove/online/offline events.

In kernel builds, the header aggregates FC protocol, link, name-server, FLA, FC-AL, transport control, error, ioctl, FCP, DDI, and devctl headers.

## Research Notes

This header is foundational for the illumos FC storage stack. It ties FC transport protocol types to SCSI/FCP consumers and supplies the kernel include surface used by FCA drivers such as `emlxs` and `qlc`.
