# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtp.c

This snoopy module formats RTP headers.

Key behavior:
- Requires the 12-byte minimum RTP header and validates CSRC list length.
- Prints version, extension bit, CSRC count, sequence number, timestamp, and SSRC.
- Prints each CSRC value and advances the message pointer past the CSRC list.
- Terminal decoder with no payload demux.

Research notes:
- Marker/payload type byte is named `marker` in the struct but is not printed.
