# File Research: sources/os/bsd/openbsd-src/sbin/route/keywords.h

This generated header defines the command/modifier keyword table used by `route.c`.

Key contents:
- `struct keytab { char *kt_cp; int kt_i; }`.
- `enum` values from `K_NULL` through `K_SWAP`.
- Sorted `keywords[]` array mapping strings such as `add`, `delete`, `flush`, `inet6`, `mpls`, `prefixlen`, `sourceaddr`, and `nameserver` to enum constants.

Behavior and integration:
- `route.c` uses `bsearch()` over `keywords[]`, so the table must remain sorted.
- Covers top-level commands, route flags, address-family modifiers, metrics, MPLS operations, route priorities, BFD toggles, and proposal commands.

Risk notes:
- Manual edits can desynchronize this file from `keywords.sh`.
- Adding a keyword without preserving sorted order breaks binary search lookup.
