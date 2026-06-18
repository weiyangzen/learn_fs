# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.c

This is the main user-space PPP implementation for Plan 9/9front. It implements PPP framing, LCP/IPCP/IPv6CP/CCP negotiation, PAP/CHAP authentication, optional TCP header compression, optional packet compression, link quality reporting, and attachment to Plan 9’s packet IP interface.

Important entry points are `main`, `pppopen`, `pppread`, and `pppwrite`. `main` parses modem/device/network/auth/compression options, opens the media endpoint, starts an `rc` helper pipe, then forks into the PPP engine. `pppopen` initializes addresses, media fds, interface metadata, PPP state, and runs the media input loop. `pppread` consumes PPP frames from the media and returns IP/IPv6 payloads. `pppwrite` accepts IP packets from the Plan 9 packet interface and sends PPP frames.

The file has several intertwined state machines. `Pstate` instances drive LCP, CCP, IPCP, and IPv6CP through closed/request/ack/open states. `setphase` moves the whole link through link authentication and network phases. `config`, `getopts`, `rejopts`, and `rcv` encode and parse LCP-style options. `ppptimer` retransmits configuration requests, drives echo keepalives, authentication retry, and link-quality packets.

The frame layer supports raw packets and HDLC-style byte-stuffed framing. It computes and checks RFC 1331 FCS via `fcstab`, handles address/control and protocol-field compression, and keeps packet/byte/discard counters.

Authentication supports PAP client mode plus CHAP MD5, MS-CHAP, and MS-CHAPv2 using Plan 9 auth APIs. MS-CHAP key material feeds MPPE/MPPC style send/receive keys. Server mode sends CHAP challenges and requires successful auth before opening network protocols unless `-a` disables auth.

Network setup is Plan 9-specific. `ipopen` opens `/net/ipifc/clone`, binds the packet device, runs `ip/ipconfig` commands through an `rc` pipe, and adds/removes IPv4 and IPv6 point-to-point addresses. IPv6CP derives link-local addresses from EUI data.

Compression paths include Van Jacobson TCP header compression and CCP data compression through `Comptype`/`Uncomptype` vtables. Unknown protocols are rejected with LCP Protocol-Reject when LCP is open.

Notable details: global `dying` coordinates shutdown across rforked processes; `terminate` removes configured IP addresses and posts a note to the process group. The implementation is tightly coupled to Plan 9 fd namespaces, `/net`, `ipifc`, and auth conventions.
