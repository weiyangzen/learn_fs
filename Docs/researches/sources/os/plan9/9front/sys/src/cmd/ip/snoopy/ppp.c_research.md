# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp.c

This is the shared PPP snoopy implementation. It defines the top-level `ppp` decoder plus subprotocol `Proto` objects for IPCP, LCP, CCP, CHAP, and compressed PPP packets.

Key behavior:
- Parses optional PPP address/control bytes and one- or two-byte protocol IDs.
- Muxes PPP protocols to `ip`, VJ TCP placeholders, multilink, compressed packets, IPCP, CCP, PAP, LCP, LQM, and CHAP.
- Provides filters for PPP subprotocol selection.
- Formats LCP/IPCP/CCP configure options and termination/reset codes.
- Formats CHAP challenge/response/success/failure and compressed packet flags/count.

Research notes:
- Several `ppp_*.c` files are one-line placeholders because their `Proto` definitions live here.
- `seprintlcpopt()` lacks an explicit `break` after `Oquality`, causing fall-through to `Omagic`; this may be intentional display aggregation or a formatting bug.
