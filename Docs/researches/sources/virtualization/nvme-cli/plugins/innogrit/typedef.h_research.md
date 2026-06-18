# File Research: sources/virtualization/nvme-cli/plugins/innogrit/typedef.h

This header contains Innogrit-specific constants and binary layouts used by `innogrit-nvme.c`.

Constants:
- Return codes: `IG_SUCCESS`, `IG_UNSUPPORT`, `IG_ERROR`.
- Vendor opcodes: `NVME_VSC_GET_EVENT_LOG`, `NVME_VSC_GET`, `NVME_VSC_TYPE1_GET`.
- Function selector: `VSC_FN_GET_CDUMP`.
- Signatures: `IGVSC_SIG`, `EVLOG_SIG`, `SRB_SIGNATURE`.
- Utility constants: terminal clear-line escape `XCLEAN_LINE`, `SIZE_MB`.

Structures:
- `evlg_flush_hdr`: event-log chunk header with signature, firmware version/type, project, trace count, CRC, and reserved words.
- `eventlog`: simple event entry with millisecond timestamp and seven parameters.
- `drvinfo_t`: 512-byte-ish drive-info structure used for VSC-type detection; includes signature, SoC/NAND/DDR/firmware/build metadata, clocks, NAND geometry, SPI/ROM info, and reserved padding.
- `cdump_pack`: cdump pack length and 8-byte firmware version.
- `cdumpinfo`: cdump metadata signature, pack count, and up to 32 `cdump_pack` records.

Role in the subsystem:
- This is not a generic typedef header; it is the protocol contract for Innogrit vendor admin commands and log payload parsing.
