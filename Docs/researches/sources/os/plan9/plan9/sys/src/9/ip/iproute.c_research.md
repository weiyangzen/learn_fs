# File Research: sources/os/plan9/plan9/sys/src/9/ip/iproute.c

Implements IPv4 and IPv6 route tables, lookup, readout, and route control writes.

Key responsibilities:
- Stores routes in per-bucket balanced range trees with `left`, `right`, and `mid` branches for disjoint and nested ranges.
- Keeps global freelists for IPv4 and IPv6 route node allocation.
- Adds IPv4 routes with `v4addroute` and IPv6 routes with `v6addroute`, computing address ranges from masks and inserting into all affected root buckets.
- Handles equal routes by superseding non-interface routes or refcounting interface routes.
- Deletes routes with `v4delroute`/`v6delroute`, reinserting child subtrees when a node is removed.
- Looks up longest/nested matching routes with route-generation caching in `Conv`.
- Resolves stale route interface pointers by finding the appropriate `Ipifc`.
- Converts routes to printable address/mask/gateway/type/tag/interface records.
- `routeread` walks both IPv4 and IPv6 route forests for `/net/iproute`.
- `routewrite` supports `flush`, `remove`, `add`, `tag`, and `route` control commands.
- Propagates route changes to interface media hooks.

Notable design:
- Route tags are four-character fields carried by channel `IPaux`.
- IPv4 lookups are also used for IPv4-mapped IPv6 addresses.
