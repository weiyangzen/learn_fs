# sources/test-tools/strace/src/xlat/isdn_protocols.in

Purpose: `isdn_protocols.in` is a strace xlat input table for ISDN constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/linux/mISDNif.h`, and the declared prefix is `ISDN_P_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#From include/linux/mISDNif.h`, `#Prefix ISDN_P_`. Generation behavior is default xlat generation semantics. Representative constants are `ISDN_P_BASE`, `ISDN_P_TE_S0`, `ISDN_P_NT_S0`, `ISDN_P_TE_E1`, `ISDN_P_NT_E1`, `ISDN_P_LAPD_TE`, `ISDN_P_LAPD_NT`, `ISDN_P_B_RAW`, ... (13 total), `ISDN_P_B_L2DTMF`, `ISDN_P_B_L2DSP`, `ISDN_P_B_L2DSPHDLC`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding ISDN arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/linux/mISDNif.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`ISDN_P_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for ISDN. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 21 source lines, 13 data rows, and value style: All 13 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: those two are present in include/linux/mISDNif.h but are not handled during; socket creation.; ISDN_P_B_T30_FAX	0x27; ISDN_P_B_MODEM_ASYNC	0x28.
