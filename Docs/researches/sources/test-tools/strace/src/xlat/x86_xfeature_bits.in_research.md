# sources/test-tools/strace/src/xlat/x86_xfeature_bits.in

Purpose: `x86_xfeature_bits.in` is a strace xlat input table for x86 CPU feature constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `arch/x86/include/asm/fpu/types.h`, and the declared prefix is `XFEATURE_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#value_indexed`, `#From arch/x86/include/asm/fpu/types.h`, `#Prefix XFEATURE_`. Generation behavior is `#value_indexed`. Representative constants are `XFEATURE_FP`, `XFEATURE_SSE`, `XFEATURE_YMM`, `XFEATURE_BNDREGS`, `XFEATURE_BNDCSR`, `XFEATURE_OPMASK`, `XFEATURE_ZMM_Hi256`, `XFEATURE_Hi16_ZMM`, ... (14 total), `XFEATURE_LBR`, `XFEATURE_XTILE_CFG`, `XFEATURE_XTILE_DATA`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding x86 CPU feature arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `arch/x86/include/asm/fpu/types.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`XFEATURE_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for x86 CPU feature. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 22 source lines, 14 data rows, and value style: All 14 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: XFEATURE_RSRVD_COMP_11		11; XFEATURE_RSRVD_COMP_12		12; XFEATURE_RSRVD_COMP_13		13; XFEATURE_RSRVD_COMP_14		14.
