# sources/test-tools/strace/src/xlat/tcp_state_flags.in

Purpose: `tcp_state_flags.in` is a strace xlat input table for TCP constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/net/tcp_states.h`, and the declared prefix is `TCP_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#From include/net/tcp_states.h`, `#Prefix TCP_`. Generation behavior is default xlat generation semantics. Representative constants are `1<<TCP_ESTABLISHED`, `1<<TCP_SYN_SENT`, `1<<TCP_SYN_RECV`, `1<<TCP_FIN_WAIT1`, `1<<TCP_FIN_WAIT2`, `1<<TCP_TIME_WAIT`, `1<<TCP_CLOSE`, `1<<TCP_CLOSE_WAIT`, ... (13 total), `1<<TCP_CLOSING`, `1<<TCP_NEW_SYN_RECV`, `1<<TCP_BOUND_INACTIVE`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding TCP arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/net/tcp_states.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`TCP_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for TCP. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 16 source lines, 13 data rows, and value style: All 13 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: this file should be included after xlat/tcp_states.h.
