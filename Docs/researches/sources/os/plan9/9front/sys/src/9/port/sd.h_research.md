# File Research: sources/os/plan9/9front/sys/src/9/port/sd.h

Common storage-device framework header.

Key contents:
- Defines permissions, partitions, extra files, storage units, controllers (`SDev`), controller interface (`SDifc`), requests (`SDreq`), and MMC/SD host controller interface (`SDio`).
- Defines status values, sense flags, max I/O size, partition limits, and read/write directions.
- Provides DMA-friendly allocation macros `sdmalloc` and `sdfree`.
- Declares MMC/SD command descriptors and SDio registration/annex functions.
- Declares `devsd.c` helpers for device registration, fake SCSI, fake SCSI read/write translation, and controller annexing.
- Declares SCSI verify/online/bio helpers.

Role:
- Unifies SCSI-like storage devices, ATA/AoE/loop/MMC transports, and `devsd` user-visible storage namespace.

Notable constraints:
- `SDunit.inquiry` and `sense` are sized to fixed SCSI-compatible buffers.
- `SDifc` mixes block-I/O, raw request, control, pnp/probe, and top-level control hooks.
