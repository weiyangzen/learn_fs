# sources/test-tools/strace/src/xlat/smc_states.in

Purpose: `smc_states.in` is a strace xlat input table for SMC socket constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `net/smc/smc.h`, and the declared prefix is `SMC_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#From net/smc/smc.h`, `#Prefix SMC_`. Generation behavior is default xlat generation semantics. Representative constants are `SMC_ACTIVE`, `SMC_INIT`, `SMC_CLOSED`, `SMC_LISTEN`, `SMC_PEERCLOSEWAIT1`, `SMC_PEERCLOSEWAIT2`, `SMC_APPFINCLOSEWAIT`, `SMC_APPCLOSEWAIT1`, `SMC_APPCLOSEWAIT2`, `SMC_PEERFINCLOSEWAIT`, `SMC_PEERABORTWAIT`, `SMC_PROCESSABORT`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding SMC socket arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `net/smc/smc.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`SMC_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for SMC socket. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 14 source lines, 12 data rows, and value style: All 12 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
