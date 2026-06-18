# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnarea.c

Tracks DNS authority areas owned by this server and delegated subareas.

Key elements:
- Defines global `Area *owned` and `Area *delegated`.
- `nameinarea` finds the longest matching suffix area for a domain name.
- `inmyarea` returns the owned area containing a name unless a longer delegated subarea contains it.
- `addarea` creates an `Area` from an SOA RR, placing it in either `owned` or `delegated` depending on the ndb tuple value.
- `freeareas` releases all areas and their copied SOA records.

Notable behavior:
- Areas are sorted by decreasing name length so more-specific areas are checked first.
- Each `Area` stores a copied SOA RR, and new areas default to `neednotify = 1`.
- Delegation is represented as an area with a non-empty tuple value.

Risks and quirks:
- `addarea` logs `"delegated"` only when the insertion pointer is literally `&delegated`; after list traversal this comparison may not reflect the original list.
- The SOA owner `DN` must remain valid through the DN cache lifecycle, as noted by the comment.
