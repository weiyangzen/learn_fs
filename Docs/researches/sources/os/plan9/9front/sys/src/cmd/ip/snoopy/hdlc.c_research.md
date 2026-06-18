# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/hdlc.c

This module frames and decodes HDLC-style PPP byte streams for snoopy. It duplicates the PPP FCS table and constants used by the PPP implementation.

The protocol view only recognizes PPP address/control bytes as the mux key and demuxes to `ppp`. `p_filter` compares the first two bytes. `p_seprint` consumes those bytes and demuxes.

The custom `p_framer` reads from an fd into a static buffer, searches for HDLC frame delimiters, unescapes bytes, computes PPP FCS, drops bad frames with a diagnostic, and returns complete good frames to snoopy.

This framer is stream-oriented and maintains static buffered state across calls.
