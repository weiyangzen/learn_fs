# sources/test-tools/strace/src/xlat/pr_ppc_dexcr_aspects.in

Purpose: `pr_ppc_dexcr_aspects.in` is a strace xlat input table for prctl constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/prctl.h`, and the declared prefix is `PR_PPC_DEXCR_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#value_indexed`, `#From include/uapi/linux/prctl.h`, `#Prefix PR_PPC_DEXCR_`. Generation behavior is `#value_indexed`. Representative constants are `PR_PPC_DEXCR_SBHE`, `PR_PPC_DEXCR_IBRTPD`, `PR_PPC_DEXCR_SRAPD`, `PR_PPC_DEXCR_NPHIE`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding prctl arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/prctl.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`PR_PPC_DEXCR_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for prctl. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 7 source lines, 4 data rows, and value style: All 4 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
