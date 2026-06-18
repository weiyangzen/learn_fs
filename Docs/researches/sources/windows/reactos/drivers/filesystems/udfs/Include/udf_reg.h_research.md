# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_reg.h

## Purpose
Centralizes UDFS service names, registry paths, object names, filesystem titles, defaults, tunable registry value names, and companion executable names.

## Main Contents
- Defines service names such as `DwUdf`, `DwCdrw`, and `DwUdfMgr`.
- Defines service/parameter registry paths and CDROM class filter location.
- Defines NT object names for UDF filesystem devices, recognizers, DOS device link, and CDFS/UDFS recognizer names.
- Defines media-specific filesystem title strings, with `PRETEND_NTFS` overriding titles to `NTFS`.
- Defines defaults such as volume label, blank media label, max shell label length, and per-media default registry subkeys.
- Defines many registry tunables: allocation mode, UID/GID, packing thresholds, flush periods, delayed update/eject periods, FSP threads, readahead, sparse threshold, verify-on-write, timestamp/attribute update policies, read-only handling, compatibility flags, cache behavior, forced mount, autoformat, and mount filters.
- Defines formatter/register executable names.

## Notes
Some names preserve historical misspellings such as `ReadAheadGranlarity`, `IgnoreSequantialIo`, and `PartitialDamagedVolumeAction`; changing them would break registry compatibility.
