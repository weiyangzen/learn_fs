# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sddef.h

## Purpose
Private definition header for the illumos SCSI disk/CD target driver, covering soft-state, open maps, block-size conversion, read-modify-write support, thin provisioning, reservations, FMA telemetry, retry/throttle policy, power management, kstats, CD/DVD quirks, VPD pages, and configuration properties.

## Main Interfaces
- Minor/partition macros: `SDUNIT`, `SDPART`, `MAXPART`, `SD_GET_INSTANCE_FROM_BUF`.
- Open-count structures: `ocinfo`, `ocmap`.
- `struct sd_lun`: main disk soft-state with SCSA device pointer, request-sense resources, I/O queues, block geometry, controller/interconnect data, retry/throttle state, reservations, event callbacks, kstats, flags, PM state, media watch state, RMW state, thin provisioning, block limits, failfast queues, FMA, and CMLB handle.
- Block conversion macros: `SD_BYTES2TGTBLOCKS`, `SD_BYTES2PHYBLOCKS`, `SD_TGTBLOCKS2BYTES`, `SD_SYS2TGTBLOCK`, `SD_TGT2SYSBLOCK`.
- Non-512/RMW structures: `sd_w_map`, `sd_mapblocksize_info`, RMW flags.
- Thin provisioning: `SD_THIN_PROV_ENABLED`, `SD_THIN_PROV_READ_ZEROS`, `sd_blk_limits_t`, `sd_unmapstats_t`.
- Persistent reservation structures and service action constants.
- `struct sd_xbuf`, `struct sd_uscsi_info`, `sd_ssc_t`, FMA assessment enums, `struct sd_fm_internal`.
- Debug/logging, kstat update, retry, throttle, state, power-management, VPD, CD-ROM, and platform partition macros.

## Dependencies And Relationships
Includes `sys/dktp/fdisk.h`, `sys/note.h`, `sys/mhd.h`, and `sys/cmlb.h`, and depends heavily on SCSA, DKIO, CMLB, FMA, kstat, and buffer-layer types included by consumers.

## Research Notes
This file is a dense private map of the `sd` driver’s behavior. It distinguishes system, target, and physical block sizes; supports non-512-byte removable media through RMW; and carries extensive compatibility quirks for SCSI disks and CD/DVD devices.

## Notable Risks
- Block-size conversion and RMW range locking are data-integrity sensitive.
- Reservation/failfast state affects clustered storage correctness.
- `sd_xbuf` layering requires each layer to restore `xb_private` correctly.
- Power-management and watch-token state crosses suspend/resume, media changes, and in-flight I/O.
- Many flags encode historical device quirks; removing or renumbering them can break configured systems.
