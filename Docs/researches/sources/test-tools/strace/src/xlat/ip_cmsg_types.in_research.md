# sources/test-tools/strace/src/xlat/ip_cmsg_types.in

Purpose: `ip_cmsg_types.in` is a strace xlat input table for IP socket constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/in.h`, and the declared prefix is `IP_ SCM_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#From include/linux/socket.h`, `#From include/uapi/linux/in.h`, `#Prefix IP_ SCM_`. Generation behavior is default xlat generation semantics. Representative constants are `IP_TOS`, `IP_TTL`, `IP_RECVOPTS`, `IP_RETOPTS`, `IP_PKTINFO`, `IP_RECVERR`, `IP_ORIGDSTADDR`, `IP_CHECKSUM`, `IP_PROTOCOL`, `SCM_SECURITY`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding IP socket arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/in.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`IP_ SCM_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for IP socket. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 13 source lines, 10 data rows, and value style: 9 rows carry explicit expressions or values and 1 rows rely on the macro value supplied by the including headers. Inline category comments: none.
