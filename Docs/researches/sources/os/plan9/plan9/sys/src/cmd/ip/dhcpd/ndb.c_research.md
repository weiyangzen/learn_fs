# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ndb.c

`ndb.c` integrates DHCP server decisions with Plan 9’s network database.

Key behavior:
- `opendb` lazily opens `ndbfile` and periodically reloads when changed.
- `findlifc` finds a local interface whose network contains an IP.
- `forme` tests whether an IP is one of the server’s interface addresses.
- `lookupip` uses `ndbipinfo` to populate `Info` for a given IP, including mask, gateway, fs/auth/tftp servers, boot files, domain, DHCP group, vendor, rootpath, and Ethernet.
- `lookup` maps a BOOTP client to host info, preferring `ciaddr` when valid, otherwise hardware address lookup.
- `lookupinfo`, `lookupserver`, and `lookupname` expose NDB result helpers for option construction.

Important dependencies:
- Uses global `ipifcs`, `now`, `blog`, `debug`, and `ndbfile`.
- Relies on Plan 9 `ndb` APIs.

Notable risks/quirks:
- Comments note Ethernet matching is likely wrong for machines with multiple Ethernet addresses.
