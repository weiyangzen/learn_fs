# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ttls.c

`snoopy` EAP-TTLS payload header formatter.

Key behavior:
- Parses TTLS flags and optional total length field.
- Prints version bits, S/M/L flag letters, optional total length, remaining data length, and ACK indication for empty no-flag packets.
- Demuxes remainder to dump so payload bytes are visible.

Integration:
- Reached from EAP subtype TTLS.

Risks and notes:
- Only handles TTLS outer flag/length wrapper; no TLS decoding.
