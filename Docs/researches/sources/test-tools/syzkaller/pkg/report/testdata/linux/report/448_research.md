# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/448

Purpose: golden fixture for a kernel BUG caused by an skb over-panic in PF_KEY/XFRM output. Expected title is `kernel BUG in pfkey_send_acquire`, type is `BUG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser consumes `TYPE: BUG` and panic status through `ParseTest`. Kernel frames include `skb_panic`, `skb_put.cold`, `pfkey_send_acquire`, `km_query`, `xfrm_state_find`, `xfrm_tmpl_resolve`, `xfrm_lookup_with_ifid`, `ip_route_output_flow`, `udp_sendmsg`, and `udpv6_sendmsg`.

Control flow: the console starts with `skbuff: skb_over_panic`, then a `kernel BUG at net/core/skbuff.c:108`, invalid opcode, full trace, repeated RIP register dump, and a fatal-exception panic. The parser must report the semantic caller `pfkey_send_acquire`, not the low-level `skb_panic`.

State and persistence behavior: no runtime state is changed by the fixture. The persistent expectation verifies that panic-on-fatal-exception is captured and that low-level skb helpers are treated as less guilty than PF_KEY.

Dependencies and integration points: depends on Linux BUG/oops regexes, stack guilty-frame selection, and panic detection. It integrates skbuff, PF_KEY, XFRM, and UDPv6 send paths into parser coverage.

Risks: the first RIP is `skb_panic`, so naive top-frame title selection would be less useful. Interleaved kobject messages test report boundary handling.

Test signals: `skb_over_panic`, `kernel BUG at net/core/skbuff.c:108`, stack `skb_put.cold -> pfkey_send_acquire -> km_query -> xfrm_state_find`, and `Kernel panic - not syncing: Fatal exception`.
