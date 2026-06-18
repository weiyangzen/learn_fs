# sources/test-tools/strace/src/xlat/inet6_devconf_indices.in

Purpose: `inet6_devconf_indices.in` is a strace xlat input table for IPv6 device configuration constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/ipv6.h`, and the declared prefix is `DEVCONF_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#value_indexed`, `#From include/uapi/linux/ipv6.h`, `#Prefix DEVCONF_`. Generation behavior is `#value_indexed`. Representative constants are `DEVCONF_FORWARDING`, `DEVCONF_HOPLIMIT`, `DEVCONF_MTU6`, `DEVCONF_ACCEPT_RA`, `DEVCONF_ACCEPT_REDIRECTS`, `DEVCONF_AUTOCONF`, `DEVCONF_DAD_TRANSMITS`, `DEVCONF_RTR_SOLICITS`, ... (60 total), `DEVCONF_ACCEPT_UNTRACKED_NA`, `DEVCONF_ACCEPT_RA_MIN_LFT`, `DEVCONF_FORCE_FORWARDING`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding IPv6 device configuration arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/ipv6.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`DEVCONF_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for IPv6 device configuration. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 63 source lines, 60 data rows, and value style: All 60 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
