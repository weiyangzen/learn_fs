<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267

## Purpose
This fixture verifies soft-lockup parsing in IPv6 receive processing. The expected title is `BUG: soft lockup in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log is a watchdog soft lockup with a network receive stack. Parser paths include soft-lockup report matching, hang alt generation, and meaningful frame selection. Important symbols include `tun_get_user`, `_decode_session6`, `__xfrm_decode_session`, `icmpv6_route_lookup`, `icmp6_send`, `ip6_input_finish`, `ip6_input`, `ip6_rcv_finish`, `ipv6_rcv`, `__netif_receive_skb_core`, `napi_gro_frags`, `tun_chr_write_iter`, and `__x64_sys_writev`.

## Control Flow
The reporter sees the watchdog line, register dump, and call trace. The selected title frame should be `ipv6_rcv` in the network stack, not earlier tun/xfrm helper frames or syscall wrappers.

## State and Persistence Behavior
No mutable state exists. The persistent contract is title, alt title, and HANG type over a 55-line log.

## Dependencies and Integration Points
It depends on Linux soft-lockup patterns and stack parser heuristics for network paths.

## Risks and Edge Cases
Network receive traces are deep and include tun, xfrm, ICMPv6, and syscall frames; frame-priority changes can retitle the report.

## Test Signals
The parse must return `BUG: soft lockup in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267 -->
