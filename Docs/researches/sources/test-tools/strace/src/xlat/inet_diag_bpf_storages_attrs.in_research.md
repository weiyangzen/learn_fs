# sources/test-tools/strace/src/xlat/inet_diag_bpf_storages_attrs.in

Purpose: `inet_diag_bpf_storages_attrs.in` is a strace xlat input table for INET socket diagnostics constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/sock_diag.h`, and the declared prefix is `SK_DIAG_BPF_STORAGE_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#value_indexed`, `#unconditional`, `#From include/uapi/linux/sock_diag.h`, `#Prefix SK_DIAG_BPF_STORAGE_`. Generation behavior is `#unconditional`, `#value_indexed`. Representative constants are `SK_DIAG_BPF_STORAGE_REP_NONE`, `SK_DIAG_BPF_STORAGE`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding INET socket diagnostics arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/sock_diag.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`SK_DIAG_BPF_STORAGE_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for INET socket diagnostics. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 6 source lines, 2 data rows, and value style: All 2 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
