# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pptp.c

PPTP client that negotiates the control channel, carries PPP over GRE, and launches Plan 9 PPP.

Key behavior:
- Uses libthread and Plan 9 processes/channels for control, GRE receive, PPP receive, and timer loops.
- Implements RFC 2637 control operations for start, echo, call-out request/response, and stop-on-fatal.
- `pptpctlproc()` reads length-prefixed control messages, validates magic/type, responds to echo requests, and forwards expected replies through a channel.
- `grereadproc()` validates GRE source/destination/protocol, records ACKs, reorders a single swapped packet pair, writes PPP payloads to the PPP pipe, and schedules ACKs.
- `pppreadproc()` wraps outgoing PPP payloads in GRE/PPTP headers with sequence and ack numbers.
- `gretimeoutproc()` drives ticks, server timeout, and echo requests.
- `pushppp()` forks `/bin/ip/ppp -C -m1450` on the tunnel stream.

Integration:
- Dials TCP service `pptp`, derives local/remote IPs from the TCP connection directory, then dials GRE toward the peer.
- Uses `/bin/ip/ppp` for PPP negotiation/authentication.

Risks and notes:
- `waitacks()` is disabled by comments, so outgoing send-window enforcement is effectively inactive.
- `tcallout()` appears to read `remid` and `remwin` from the transmit packet rather than the received reply, which is suspicious.
- GRE ACK-only packet writes use `hnputs()` for an apparent sequence/ack field in `sendack()`, while other paths use long stores.
