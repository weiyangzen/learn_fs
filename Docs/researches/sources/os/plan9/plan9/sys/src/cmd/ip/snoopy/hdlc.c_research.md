# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/hdlc.c

`snoopy` HDLC/PPP framing decoder and framer.

Key behavior:
- Contains PPP FCS lookup table and HDLC frame constants.
- `p_framer()` reads byte stream until frame delimiter, unescapes bytes, validates PPP FCS, and returns a decoded frame.
- Decoder recognizes PPP address/control bytes and demuxes to `ppp`.
- Formats no additional fields beyond advancing past address/control.

Integration:
- Can be selected as root protocol/framer for HDLC byte streams.

Risks and notes:
- Bad FCS frames are printed to stdout and skipped.
- Static input buffer makes the framer stateful and non-reentrant.
