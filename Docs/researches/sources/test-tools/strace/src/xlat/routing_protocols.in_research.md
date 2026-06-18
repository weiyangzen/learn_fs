# sources/test-tools/strace/src/xlat/routing_protocols.in

Purpose: `routing_protocols.in` is a strace xlat input table for routing netlink constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/rtnetlink.h`, and the declared prefix is `RTPROT_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#sorted sort -k2,2n`, `#From include/uapi/linux/rtnetlink.h`, `#Prefix RTPROT_`. Generation behavior is `#unconditional`, `#sorted sort -k2,2n`. Representative constants are `RTPROT_UNSPEC`, `RTPROT_REDIRECT`, `RTPROT_KERNEL`, `RTPROT_BOOT`, `RTPROT_STATIC`, `RTPROT_GATED`, `RTPROT_RA`, `RTPROT_MRT`, ... (24 total), `RTPROT_OSPF`, `RTPROT_RIP`, `RTPROT_EIGRP`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding routing netlink arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/rtnetlink.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`RTPROT_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for routing netlink. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`. The sorted directive is a test signal: row order is intentional and should remain compatible with the requested sort.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 28 source lines, 24 data rows, and value style: All 24 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
