# sources/test-tools/strace/src/xlat/keyctl_pkey_ops.in

Purpose: `keyctl_pkey_ops.in` is a strace xlat input table for keyctl constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/keyctl.h`, and the declared prefix is `KEYCTL_SUPPORTS_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#From include/uapi/linux/keyctl.h`, `#Prefix KEYCTL_SUPPORTS_`. Generation behavior is `#unconditional`. Representative constants are `KEYCTL_SUPPORTS_ENCRYPT`, `KEYCTL_SUPPORTS_DECRYPT`, `KEYCTL_SUPPORTS_SIGN`, `KEYCTL_SUPPORTS_VERIFY`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding keyctl arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/keyctl.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`KEYCTL_SUPPORTS_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for keyctl. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 7 source lines, 4 data rows, and value style: All 4 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
