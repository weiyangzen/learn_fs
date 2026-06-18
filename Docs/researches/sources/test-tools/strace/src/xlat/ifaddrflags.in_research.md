# sources/test-tools/strace/src/xlat/ifaddrflags.in

Purpose: `ifaddrflags.in` is a strace xlat input table for interface address flags constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/if_addr.h`, and the declared prefix is `IFA_F_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#From include/uapi/linux/if_addr.h`, `#Prefix IFA_F_`. Generation behavior is `#unconditional`. Representative constants are `IFA_F_SECONDARY`, `IFA_F_NODAD`, `IFA_F_OPTIMISTIC`, `IFA_F_DADFAILED`, `IFA_F_HOMEADDRESS`, `IFA_F_DEPRECATED`, `IFA_F_TENTATIVE`, `IFA_F_PERMANENT`, `IFA_F_MANAGETEMPADDR`, `IFA_F_NOPREFIXROUTE`, `IFA_F_MCAUTOJOIN`, `IFA_F_STABLE_PRIVACY`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding interface address flags arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/if_addr.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`IFA_F_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for interface address flags. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 15 source lines, 12 data rows, and value style: All 12 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
