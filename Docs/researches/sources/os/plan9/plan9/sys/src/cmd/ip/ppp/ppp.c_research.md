# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.c

Main PPP implementation: HDLC-like framing, LCP/IPCP/CCP negotiation, CHAP/PAP authentication, IP interface binding, packet forwarding, compression integration, link quality monitoring, modem/chat handling, and CLI.

Key behavior:
- `pppopen` initializes a `PPP` instance, stores media fds/IP preferences, starts media input processing, and enters LCP negotiation.
- `init`, `setphase`, `pinit`, `newstate` drive PPP phases and protocol state machines for LCP, authentication, network protocols, and termination.
- `getframe` reads PPP frames, handles optional HDLC framing, escape decoding, FCS verification, address/control compression, and protocol extraction.
- `putframe` serializes PPP frames, applies protocol/address compression when negotiated, escapes control characters, appends FCS, and writes to media.
- `config`, `getopts`, `rejopts`, and `rcv` implement Configure-Request/Ack/Nak/Rej processing for LCP, CCP, and IPCP.
- IPCP supports local/remote IPv4 address negotiation, DNS/WINS options for primary links, and VJ TCP header compression.
- CCP supports MPPC and hooks compression/uncompression virtual tables.
- `ipopen` binds a Plan 9 `pkt` interface, configures point-to-point local/remote addresses, sets default route if primary, starts `ipinproc`, and rendezvous-signals configuration complete.
- `pppread` dispatches inbound frames by protocol: LCP, CCP, IPCP, IP, LQM, CHAP, PAP, VJ TCP, compressed data, and protocol rejects.
- `pppwrite` sends outbound IP, applying VJ and MPPC compression when negotiated.
- `ipinproc` reads packets from the Plan 9 packet interface and sends them over PPP.
- `mediainproc` reads PPP IP packets and writes them to the packet interface, enforcing source address on server links.
- LQM support is in `getlqm` and `putlqm`.
- CHAP/PAP:
  - `chapinit` sends server challenges.
  - `getchap` handles CHAP challenge/response/success/failure for MD5 and MS-CHAP, derives MPPE/MPPC key material for MS-CHAP.
  - `putpaprequest`, `papinit`, and `getpap` implement client-side PAP auth flow.
- `connect` supports manual modem interaction or scripted chat file send/expect sequences.
- `main` parses PPP CLI options, opens serial/dial/stdin media, configures serial control settings, optionally runs chat/user interaction, starts PPP, waits for IP configuration, and publishes NDB if primary.

Integration points:
- Central user of `ppp.h`, `block.c`, `compress.c`, `mppc.c`, `ipaux.c`, Plan 9 auth/factotum APIs, `/net/ipifc`, `/net/ndb`, and serial control files.
- `ipconfig/ppp.c` invokes this binary for PPP-backed interface configuration.

Risks and notes:
- `nipifcs` appears to loop `for(lifc = ifc->lifc; ...)` instead of `nifc->lifc`, likely a bug in interface counting.
- Global `dying`, `server`, `primary`, `debug`, etc. are process-wide and shared by forked processes using `RFMEM`.
- Authentication has server CHAP support and client PAP/CHAP response support; PAP auth requests as server are logged unsupported.
