# sources/test-tools/strace/src/xlat/icmp_filter_flags.in

Purpose: `icmp_filter_flags.in` is a strace xlat input table for ICMP constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/icmp.h`, and the declared prefix is `ICMP_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#value_indexed`, `#From include/uapi/linux/icmp.h`, `#Prefix ICMP_`. Generation behavior is `#value_indexed`. Representative constants are `ICMP_ECHOREPLY`, `ICMP_DEST_UNREACH`, `ICMP_SOURCE_QUENCH`, `ICMP_REDIRECT`, `ICMP_ECHO`, `ICMP_TIME_EXCEEDED`, `ICMP_PARAMETERPROB`, `ICMP_TIMESTAMP`, ... (13 total), `ICMP_INFO_REPLY`, `ICMP_ADDRESS`, `ICMP_ADDRESSREPLY`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding ICMP arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/icmp.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`ICMP_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for ICMP. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 16 source lines, 13 data rows, and value style: All 13 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
