# sources/test-tools/strace/src/xlat/uring_napi_tracking_strategies.in

Purpose: `uring_napi_tracking_strategies.in` is a strace xlat input table for io_uring constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/io_uring.h`, and the declared prefix is `IO_URING_NAPI_TRACKING_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#value_indexed`, `#From include/uapi/linux/io_uring.h`, `#Prefix IO_URING_NAPI_TRACKING_`. Generation behavior is `#unconditional`, `#value_indexed`. Representative constants are `IO_URING_NAPI_TRACKING_DYNAMIC`, `IO_URING_NAPI_TRACKING_STATIC`, `IO_URING_NAPI_TRACKING_INACTIVE`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding io_uring arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/io_uring.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`IO_URING_NAPI_TRACKING_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for io_uring. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 7 source lines, 3 data rows, and value style: All 3 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
