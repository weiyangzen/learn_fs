# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/tcp.c

This snoopy module decodes and filters TCP packets.

Key behavior:
- Filters support source port (`s`), destination port (`d`), and either port (`a`/`sd`).
- Muxes DNS and 9P for known TCP ports.
- Parses header length, flags, sequence/ack numbers, window, checksum, and common TCP options.
- Recognizes MSS and window-scale options; unknown options are hex-dumped.
- Special-cases DNS-over-TCP by skipping the two-byte DNS length field before handing payload to DNS.

Research notes:
- `PseudoHdr` is defined but unused here.
- Header length handling relies on the packed flag/header-length word.
