# sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp.h

## Purpose

Defines the TCP protocol header, socket option numbers, TCP diagnostic/statistics structures, TCP MD5 and TCP-AO option payloads, and zero-copy receive ABI. strace uses it to decode `setsockopt`, `getsockopt`, inet diagnostic attributes, and raw TCP header-related constants.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`, `asm/byteorder.h`, and `linux/socket.h`. Key exports are `struct tcphdr`, endian-specific flag bitfields, `union tcp_word_hdr`, `tcp_flag_word`, TCP flag constants, MSS defaults, socket options from `TCP_NODELAY` through `TCP_DELACK_MAX_US`, repair mode constants, `struct tcp_repair_opt`, `tcp_repair_window`, queue ids, fastopen failure enum, `TCPI_OPT_*`, congestion state enum and flags, ECN/AccECN constants, and the large append-only `struct tcp_info`. Netlink timestamping statistic attributes are `TCP_NLA_*`. Security/authentication payloads include `struct tcp_md5sig`, `tcp_diag_md5sig`, `tcp_ao_add`, `tcp_ao_del`, `tcp_ao_info_opt`, `tcp_ao_getsockopt`, and `tcp_ao_repair`. `struct tcp_zerocopy_receive` defines `TCP_ZEROCOPY_RECEIVE`.

## Control Flow, State, and Integration

Runtime flows are socket options configuring TCP behavior, retrieving connection stats, repairing sequence/window state, managing authentication keys, and requesting zero-copy receive mapping. Persistent state is per-socket TCP control block state, congestion-control metrics, authentication key material, fastopen state, and receive queue mapping state.

## Risks and Test Signals

Risks include endian-specific `tcphdr` layout, append-only `tcp_info` growth, sensitive key display for MD5/AO options, bitfield packing in TCP-AO structs, and fixed-size sockaddr storage in authentication options. Test signals include named socket-option decoding, `tcp_info` field coverage, TCP-AO add/delete/get/info payloads, zero-copy receive struct output, and unknown option fallback.
