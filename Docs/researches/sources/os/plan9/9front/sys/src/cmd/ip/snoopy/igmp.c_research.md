# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/igmp.c

This module decodes IGMP packets. It defines header fields for type, timeout, checksum, and group address, with filters declared for all four but implemented only for type.

`p_seprint` prints IGMP type name, timeout, checksum, and group address. It optionally verifies checksum when `Cflag` is set.

The module is a leaf protocol and defaults remaining bytes to `dump`.
