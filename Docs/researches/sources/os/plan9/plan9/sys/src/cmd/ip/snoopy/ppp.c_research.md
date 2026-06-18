# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp.c

`snoopy` PPP decoder plus PPP control-protocol formatters.

Key behavior:
- Parses optional PPP address/control compression and compressed protocol field.
- Demuxes PPP protocol IDs to IP, VJ TCP, multilink, compressed, IPCP, CCP, password auth, LCP, LQM, and CHAP.
- Formats base PPP protocol and frame length.
- Implements pseudo-protocols:
  - `ppp_lcp`: LCP codes and options such as MTU, control map, auth, quality, magic, protocol/address compression.
  - `ppp_ipcp`: IPCP address/compression/DNS/WINS options.
  - `ppp_ccp`: CCP options and reset packets.
  - `ppp_chap`: CHAP challenge/response/success/failure.
  - `ppp_comp`: compressed data flags and counter.

Integration:
- Reached from HDLC, GRE PPTP, and PPPoE session decoders.
- Placeholder files for individual PPP pseudo-protocols refer back here.

Risks and notes:
- Option walkers require valid nonzero option lengths in most paths; LCP path explicitly checks zero length, IPCP/CCP only check bounds.
