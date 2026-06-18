# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cd.h

## Purpose

`cd.h` defines CDFS on-disc constants, raw ISO/HSG/Joliet structures, directory-entry and path-table layouts, timestamp conversion, and XA system-use metadata. It is the main wire-format header for CD-ROM filesystem parsing.

## Main Contents

- Sector constants:
  - `SECTOR_SIZE`/`CD_SECTOR_SIZE`: 2048 bytes.
  - `RAW_SECTOR_SIZE` and `XA_SECTOR_SIZE`: 2352 bytes.
  - sector masks and shift constants.

- Volume descriptor constants:
  - first descriptor sector, descriptor type values, standard IDs (`CD001`, `CDROM`), version constants, volume ID lengths.

- Raw volume descriptor structures:
  - `RAW_ISO_VD`
  - `RAW_HSG_VD`
  - `RAW_JOLIET_VD`
  - These model primary/secondary descriptors with different field ordering between ISO and HSG.

- Descriptor accessor macros:
  - `CdRvdId`, `CdRvdVersion`, `CdRvdDescType`, `CdRvdEsc`, `CdRvdVolId`, `CdRvdBlkSz`, `CdRvdPtLoc`, `CdRvdPtSz`, `CdRvdDirent`, `CdRvdVolSz`.
  - Select ISO vs HSG layout based on `VCB_STATE_HSG`.

- Directory-entry layout:
  - `RAW_DIRENT` / `RAW_DIR_REC`
  - Directory flags such as hidden, directory, associated file, and multi-extent.
  - Macros for minimum record size and flag-field selection.

- Time conversion:
  - `CdConvertCdTimeToNtTime` converts 6/7-byte CD time fields to NT time.
  - Applies ISO GMT offset when present and within the ISO range `[-48, 52]` fifteen-minute units.
  - HSG media ignores GMT offset.

- Path table layouts:
  - `RAW_PATH_ISO`
  - `RAW_PATH_HSG`
  - Macros recover ID length, XAR length, and directory location despite layout differences.

- XA system-use area:
  - `SYSTEM_USE_XA`
  - Flags for form1, form2, and digital audio extents.
  - `XA_EXTENT_TYPE` enum for cooked form1 data, mode2 form2 data, and CD audio.

## Integration

This header is consumed throughout mount, path-table parsing, dirent parsing, allocation, and XA/audio file exposure. Many higher-level helpers normalize these raw structures into `DIRENT`, `PATH_ENTRY`, and FCB fields defined in `cdstruc.h`.

## Risk Notes

- Many fields are unaligned byte arrays because CD on-disc structures are packed. Callers must use the provided copy/conversion helpers rather than direct misaligned access.
- ISO/HSG differences are hidden behind macros; using raw fields directly can break HSG media.
- Timestamp conversion relies on raw byte values and only bounds-checks GMT offset, not full date validity.
