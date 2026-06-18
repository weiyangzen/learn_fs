# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpleases.c

`dhcpleases.c` lists active DHCP leases.

Key behavior:
- Opens `binddir`, reads all directory entries, parses each name as an IP, syncs its binding, and prints leases with expiry time if still active.
- Initializes IP formatters and global `now`.
- Defines required globals `blog` and `minlease`.

Important dependencies:
- Uses `syncbinding` and `Binding` from the DHCP server database.

Notable risks/quirks:
- Reuses a stack `Binding` and relies on `syncbinding` populating it.
