# sources/test-tools/strace/src/xlat/hdio_drive_cmds.in

Purpose: `hdio_drive_cmds.in` is a strace xlat input table for HDIO/IDE constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/linux/ata.h`, and the declared prefix is `ATA_CMD_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#sorted sort -k2,2`, `#From include/linux/ata.h`, `#Prefix ATA_CMD_`. Generation behavior is `#sorted sort -k2,2`. Representative constants are `ATA_CMD_NOP`, `ATA_CMD_CFA_REQ_EXT_ERR`, `ATA_CMD_DSM`, `ATA_CMD_DEV_RESET`, `ATA_CMD_REQ_SENSE_DATA`, `ATA_CMD_RESTORE`, `ATA_CMD_PIO_READ`, `ATA_CMD_READ_LONG`, ... (93 total), `ATA_CMD_SEC_DISABLE_PASS`, `ATA_CMD_READ_NATIVE_MAX`, `ATA_CMD_SET_MAX`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding HDIO/IDE arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/linux/ata.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`ATA_CMD_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for HDIO/IDE. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`. The sorted directive is a test signal: row order is intentional and should remain compatible with the requested sort.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 96 source lines, 93 data rows, and value style: All 93 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
