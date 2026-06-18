# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ipmux.c

This module decodes packets prefixed by a 16-byte interface address, then demuxes the following payload as IPv4 or IPv6 based on the high nibble of the first payload byte.

Filters support the interface address and IP type. `p_filter` consumes the 16-byte address and compares either address bytes or payload type. `p_seprint` prints interface address, type nibble, and total length, then demuxes to `ip`, `ip6`, or `dump`.

This is useful for packet sources that include an interface address before raw IP payloads.
