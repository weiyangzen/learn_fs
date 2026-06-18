# File Research: sources/os/bsd/netbsd-src/sys/sys/cdio.h

## Scope

Defines CD-ROM, audio CD, subchannel, TOC, changer/load, and optional MMC ioctl ABI.

## APIs And Data Structures

- `union msf_lba` represents minute/second/frame, LBA, or raw address bytes.
- Defines TOC entries and subchannel headers/data with endian-dependent bitfields.
- CD ioctls support play by tracks, blocks, or MSF; read subchannel; read TOC header/entries; read session start; audio patch/volume/channel controls; pause/resume/reset/start/stop/eject/allow/prevent/close; and load/unload.
- Kernel-only buffered variants embed result buffers after request structs.
- Optional kernel or `_EXPOSE_MMC` API defines `mmc_discinfo`, MMC class/state/capability flags, `mmc_trackinfo`, `mmc_op`, and `mmc_writeparams`.

## Dependencies

- Includes `sys/ioccom.h` and `sys/endian.h`.

## Risks And Invariants

- Endian-dependent bitfield order must match device protocol layout.
- Some ioctl command numbers overlap historical commands with different structs.
- MMC section is intentionally not generally exposed to userland unless requested.
