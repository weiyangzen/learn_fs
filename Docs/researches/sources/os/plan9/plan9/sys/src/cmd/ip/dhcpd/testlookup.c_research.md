# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlookup.c

`testlookup.c` is a test utility for server lookup resolution.

Key behavior:
- Opens NDB and gets `Ipinfo` by IP or Ethernet argument.
- Implements `lookupserver` to find named server attributes directly on the host entry or recursively from subnet entries.
- Resolves server names to IPs, preferring addresses on the same subnet.
- Prints host info, then auth and DNS lookup results.

Important dependencies:
- Uses Plan 9 `ipinfo`, NDB APIs, and IP formatting.

Notable risks/quirks:
- Contains a likely inverted/buggy duplicate-name handling branch in `recursesubnet`.
- Uses global `Ndb *db`.
