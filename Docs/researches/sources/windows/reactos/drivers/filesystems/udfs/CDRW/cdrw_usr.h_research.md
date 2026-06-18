# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_usr.h

## Purpose

`cdrw_usr.h` defines the public ABI between the CD writer driver and user/kernel clients. It maps driver IOCTLs, aliases standard CDROM/DVD/storage IOCTLs, and defines packed user-facing input/output structures that convert the low-level `cdrw_hw.h` wire records into host-endian fields.

## Main Contents

- Includes `cdrw_hw.h`, `ntddcdrm.h`, `ntddcdvd.h`, `winioctl.h`, and optionally `mountmgr.h`.
- Defines `FILE_DEVICE_CDRW`, `CDRW_SIGNATURE_v1`, and `CDRW_CTL_CODE_*` helpers.
- Defines private IOCTLs for:
  - tray locking, speed control, synchronize cache, capability/media queries.
  - write mode get/set, reserve track, blank, close track/session, low-level read/write.
  - disc/track info, buffer capacity, signature, driver reset, format unit, random access mode.
  - mode sense/select, read-ahead, media-change notification, OPC, cue sheet, full TOC/PMA/session/ATIP/CD-TEXT reads.
  - device info, event status, MRW mode, read capacity, disc layout, set streaming.
- Re-exports standard CDROM/DVD/disk/storage IOCTLs where platform headers may not define them.
- Provides fallback `STORAGE_MEDIA_TYPE` and media IOCTL definitions for older environments.
- Defines input/output structs for all private IOCTLs:
  - speed, streaming, sync cache, blank, reserve track, low-level read/write, format, close, media removal, read ahead.
  - track info, disc status/info, media type/class/capability, mode sense/select, write parameters, capabilities, OPC.
  - last error, raw read, audio, TOC/session/PMA/ATIP/CD-TEXT, init/deinit, geometry, device info, event, DVD structure/key/session, disk verify, layout.
- Defines capability flags:
  - media classes and extended classes.
  - `CDRW_FEATURE_*` device workaround/feature flags.
  - `CDRW_DEV_CAPABILITY_*` media support bitmasks.
- Defines driver error codes returned by last-error queries.
- Defines registry value names and policy constants for timeout, autorun/load mode, packet size, format workaround, split sizes, simulation, speed detection, sync packets, readiness, seek workarounds, packet-on-CD-R, retry limits, DVD quirks, and default last-LBA fallbacks.

## Integration Notes

This is the stable control-plane contract for CDRW operations. Kernel code handling device control requests should interpret input/output buffers using these structures, while user tools can include the same header for compatible IOCTL calls.

## Risks And Edge Cases

- The ABI is packed with `#pragma pack(push, 1)` and uses Windows types, so structure layout compatibility is critical.
- Some conditional macros are suspicious:
  - In `CDRW_RESTRICT_ACCESS`, `CDRW_CTL_CODE_W` is defined twice.
  - `REG_BAD_DVD_LAST_LBA_NAME_USER` is duplicated.
  - Several public field names preserve typos such as `VersiomMajor`.
- `GET_DISK_LAYOUT_USER_OUT` contains a raw pointer to `MediaTrackMap`, which is fragile across user/kernel address spaces unless the IOCTL handler marshals it carefully.
- Many structs mirror low-level SCSI records but convert fields to host-endian integers; handlers must avoid mixing raw and user versions.
