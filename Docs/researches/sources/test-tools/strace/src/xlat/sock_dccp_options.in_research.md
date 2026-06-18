# sources/test-tools/strace/src/xlat/sock_dccp_options.in

Purpose: `sock_dccp_options.in` is a strace xlat input table for socket option constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/dccp.h`, and the declared prefix is `DCCP_SOCKOPT_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#sorted sort -k2,2n`, `#From include/uapi/linux/dccp.h`, `#Prefix DCCP_SOCKOPT_`. Generation behavior is `#sorted sort -k2,2n`. Representative constants are `DCCP_SOCKOPT_PACKET_SIZE`, `DCCP_SOCKOPT_SERVICE`, `DCCP_SOCKOPT_CHANGE_L`, `DCCP_SOCKOPT_CHANGE_R`, `DCCP_SOCKOPT_GET_CUR_MPS`, `DCCP_SOCKOPT_SERVER_TIMEWAIT`, `DCCP_SOCKOPT_SEND_CSCOV`, `DCCP_SOCKOPT_RECV_CSCOV`, ... (16 total), `DCCP_SOCKOPT_QPOLICY_TXQLEN`, `DCCP_SOCKOPT_CCID_RX_INFO`, `DCCP_SOCKOPT_CCID_TX_INFO`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding socket option arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/dccp.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`DCCP_SOCKOPT_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. Availability follows the usual generated-header checks unless individual rows are unconditional through included definitions.

Integration points: integrated by syscall decoders that include the generated xlat for socket option. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`. The sorted directive is a test signal: row order is intentional and should remain compatible with the requested sort.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 19 source lines, 16 data rows, and value style: All 16 rows carry explicit numeric values or expressions, so decoder output does not depend on contiguous enum ordering. Inline category comments: none.
