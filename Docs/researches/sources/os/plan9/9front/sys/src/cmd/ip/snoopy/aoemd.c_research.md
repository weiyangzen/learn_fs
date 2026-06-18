# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemd.c

This module decodes AoE mask directive records. The payload contains a reserved byte, command byte, and Ethernet address.

Filters support command and Ethernet address. Ethernet comparison reconstructs the target six-byte address from `Filter.ulv`.

`p_seprint` prints command numeric/name and Ethernet address, then stops protocol traversal. Command names are blank, add, and remove markers.
