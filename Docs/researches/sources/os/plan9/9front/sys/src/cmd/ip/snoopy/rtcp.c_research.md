# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtcp.c

This snoopy module formats RTCP sender reports plus report blocks.

Key behavior:
- Requires the minimum 28-byte sender report header.
- Validates packet length using the RTCP length field.
- Prints version, report count, packet type, SSRC, NTP/RTP timestamps, packet/octet counts, and header length.
- Iterates report blocks, printing CSRC, loss percentage/cumulative loss, highest sequence, jitter, LSR, and DLSR.
- Terminal decoder with no filters/mux.

Research notes:
- The code mutates `r->lost[0] = 0` while formatting cumulative loss, modifying the packet buffer.
