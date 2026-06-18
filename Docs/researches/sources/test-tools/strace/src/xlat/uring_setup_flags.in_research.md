# sources/test-tools/strace/src/xlat/uring_setup_flags.in

Purpose: `uring_setup_flags.in` is a strace xlat input table for io_uring constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/io_uring.h`, and the declared prefix is `IORING_SETUP_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#From include/uapi/linux/io_uring.h`, `#Prefix IORING_SETUP_`. Generation behavior is `#unconditional`. Representative constants are `IORING_SETUP_IOPOLL`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SQ_AFF`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_CLAMP`, `IORING_SETUP_ATTACH_WQ`, `IORING_SETUP_R_DISABLED`, `IORING_SETUP_SUBMIT_ALL`, ... (21 total), `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_SQE_MIXED`, `IORING_SETUP_SQ_REWIND`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding io_uring arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/io_uring.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`IORING_SETUP_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for io_uring. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 24 source lines, 21 data rows, and value style: All 21 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
