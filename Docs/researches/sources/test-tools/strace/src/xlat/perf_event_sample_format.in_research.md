# sources/test-tools/strace/src/xlat/perf_event_sample_format.in

Purpose: `perf_event_sample_format.in` is a strace xlat input table for perf event constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/perf_event.h`, and the declared prefix is `PERF_SAMPLE_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#From include/uapi/linux/perf_event.h`, `#Prefix PERF_SAMPLE_`. Generation behavior is default xlat generation semantics. Representative constants are `PERF_SAMPLE_IP`, `PERF_SAMPLE_TID`, `PERF_SAMPLE_TIME`, `PERF_SAMPLE_ADDR`, `PERF_SAMPLE_READ`, `PERF_SAMPLE_CALLCHAIN`, `PERF_SAMPLE_ID`, `PERF_SAMPLE_CPU`, ... (25 total), `PERF_SAMPLE_DATA_PAGE_SIZE`, `PERF_SAMPLE_CODE_PAGE_SIZE`, `PERF_SAMPLE_WEIGHT_STRUCT`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding perf event arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/perf_event.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`PERF_SAMPLE_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for perf event. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 27 source lines, 25 data rows, and value style: All 25 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
