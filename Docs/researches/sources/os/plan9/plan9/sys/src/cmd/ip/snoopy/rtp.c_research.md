# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtp.c

`snoopy` RTP formatter.

Key behavior:
- Parses RTP version, extension bit, CSRC count, sequence, timestamp, and SSRC.
- Prints each CSRC when present.
- Terminates protocol walk.

Integration:
- Reached from UDP demux when selected.

Risks and notes:
- Does not decode marker, payload type, extension header, padding, or payload.
