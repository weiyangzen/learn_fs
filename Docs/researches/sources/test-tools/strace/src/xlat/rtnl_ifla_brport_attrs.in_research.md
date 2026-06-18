# sources/test-tools/strace/src/xlat/rtnl_ifla_brport_attrs.in

Purpose: `rtnl_ifla_brport_attrs.in` is a strace xlat input table for rtnetlink constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/if_link.h`, and the declared prefix is `IFLA_BRPORT_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#value_indexed`, `#From include/uapi/linux/if_link.h`, `#Prefix IFLA_BRPORT_`. Generation behavior is `#unconditional`, `#value_indexed`. Representative constants are `IFLA_BRPORT_UNSPEC`, `IFLA_BRPORT_STATE`, `IFLA_BRPORT_PRIORITY`, `IFLA_BRPORT_COST`, `IFLA_BRPORT_MODE`, `IFLA_BRPORT_GUARD`, `IFLA_BRPORT_PROTECT`, `IFLA_BRPORT_FAST_LEAVE`, ... (45 total), `IFLA_BRPORT_MCAST_MAX_GROUPS`, `IFLA_BRPORT_NEIGH_VLAN_SUPPRESS`, `IFLA_BRPORT_BACKUP_NHID`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding rtnetlink arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/if_link.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`IFLA_BRPORT_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for rtnetlink. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 49 source lines, 45 data rows, and value style: All 45 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
