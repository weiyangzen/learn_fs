# File Research: sources/os/linux/linux-stable/fs/udf/Kconfig

## Summary
Defines `CONFIG_UDF_FS`, the Linux UDF filesystem build option.

## Main Responsibilities
- Exposes UDF support as tristate `UDF_FS`.
- Selects required infrastructure: `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, and `LEGACY_DIRECT_IO`.
- Documents that UDF is used for CD-ROM/DVD media, packet-written CD-RW, and removable USB disks.
- States the module name is `udf`.

## Risks
The selected dependencies match assumptions throughout the UDF implementation: buffer-head based metadata I/O, ITU-T CRC descriptor checksums, NLS filename conversion, and legacy direct I/O hooks.
