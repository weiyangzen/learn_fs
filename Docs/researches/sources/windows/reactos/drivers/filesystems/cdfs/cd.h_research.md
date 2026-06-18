# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cd.h

## Scope And Purpose

`cd.h` defines CDFS on-disc structures and constants for ISO 9660, HSG, Joliet, directory records, path-table records, CD time conversion, and XA system-use data.

Complete file read: 534 lines.

## Main Components

- Sector constants define 2048-byte logical sectors, 2352-byte raw/XA sectors, sector masks, and sector shifts.
- Volume descriptor constants define descriptor sector, descriptor types, version, standard IDs, volume ID size, root directory-entry length, and TOC data-track flags.
- `RAW_ISO_VD`, `RAW_HSG_VD`, and `RAW_JOLIET_VD` describe primary/secondary volume descriptor layouts.
- `CdRvd*` macros abstract field access across ISO and HSG volume descriptors.
- `RAW_DIRENT` overlays ISO/HSG directory records, including extent location, data length, record time, flags, interleave fields, volume sequence number, and file ID.
- Directory attribute constants define hidden, directory, associated-file, and multi-extent flags.
- `CdRawDirentFlags` selects the correct HSG or ISO flag field.
- `CdConvertCdTimeToNtTime` converts 7-byte CD timestamps into NT time and applies ISO GMT offset when valid.
- `RAW_PATH_ISO` and `RAW_PATH_HSG` describe path-table entry variants.
- `CdRawPathIdLen`, `CdRawPathXar`, and `CdRawPathLoc` abstract path-table field access across ISO/HSG layouts.
- `SYSTEM_USE_XA` and `XA_EXTENT_TYPE` define XA extension metadata and extent categories.

## Integration Points

This header is included through CDFS internals wherever raw disc structures are parsed. It relies on broader driver definitions such as `VCB_STATE_HSG`, `FlagOn`, `Add2Ptr`, `RtlTimeFieldsToTime`, and CDFS VCB/IRP context types.

## Notes

- Structures intentionally mirror unaligned on-disc layouts; helper macros avoid unsafe direct interpretation in some cases.
- CD time conversion applies GMT offsets only for ISO media and only for the valid `[-48, 52]` quarter-hour range.
- The raw directory record supports file IDs up to 255 bytes, beyond strict short-name assumptions.
