# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ippkt.c

This module is a raw IP packet discriminator. It has no extra header; it inspects the high nibble of the first byte and demuxes to IPv4 for `0x40` or IPv6 for `0x60`.

Filters support type nibble comparisons or protocol-name shorthand `ip` and `ip6`. `p_seprint` prints the detected type and sets the next protocol accordingly.

It is the simplest root for raw IP packet streams.
