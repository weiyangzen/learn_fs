# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtcp.c

`snoopy` RTCP sender-report style formatter.

Key behavior:
- Parses RTCP header, packet type, report length, sender SSRC, NTP/RTP timestamps, packet count, and octet count.
- Iterates reception report blocks and formats source, loss fraction, cumulative lost, highest sequence, jitter, last sender report, and delay since last sender report.
- Terminates protocol walk.

Integration:
- Reached from UDP demux when selected by filter/default protocol path.

Risks and notes:
- Assumes sender-report layout with 28-byte minimum, so other RTCP packet types are not generally decoded correctly.
