# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.h

This header defines the core PPP data model shared by the PPP engine and compression modules. It declares `Block`, `PPP`, `Pstate`, `Chap`, `Qualstats`, compression vtables, LCP option/message structures, and protocol constants.

`Block` is the local packet-buffer abstraction with `rptr`, `wptr`, `base`, and `lim`, plus `BLEN` and `BALLOC`. The header only declares allocation helpers; definitions live elsewhere in the PPP program set.

The large enum captures HDLC constants, PPP phases, PPP protocol numbers, LCP codes, LCP/CCP/ECP/IPCP/IPv6CP options, auth protocols, state names, timers, buffer sizes, and MTU bounds. These constants are consumed directly by `ppp.c`, `thw.c`, and related modules.

`PPP` is the central runtime object. It embeds locks, media/IP fds, Plan 9 network paths, IPv4/IPv6 negotiated/current addresses, DNS/WINS values, input/output buffers, LCP/CCP/IPCP/IPv6CP/CHAP state pointers, compression state, encryption keys, auth name, link-quality counters, and packet statistics.

The compression interface is abstracted through `Comptype` and `Uncomptype`, allowing MPPC and Thwack modules to plug into CCP without changing the main PPP state machine.

Exports include `pppread`, `pppwrite`, `pppopen`, LCP allocation/checksum helpers, TCP compression hooks, MS-CHAP key derivation, MPPC/Thwack vtables, and `netlog`.
