# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_update.c

Read completely: 219 lines.

Implements `res_nupdate()`, the high-level dynamic DNS update sender. It groups input `ns_updrec` records by discovered zone origin and class using `res_findzonecut2()`, prepends a generated SOA zone-section record for each group, marshals the update with `res_nmkupdate()`, and sends to the authoritative nameservers for that zone.

For each zone, it temporarily replaces the resolver state's configured server list with the zone's nameserver addresses, sends either unsigned with `res_nsend()` or signed with `res_nsendsigned()`, counts successful zones when the response rcode is `NOERROR`, and restores the original server list.

Cleanup removes generated zone-section records and frees group objects. Partial success is possible: earlier zones can be updated before a later zone fails, and the function returns the number of zones updated rather than a strict negative error code.
