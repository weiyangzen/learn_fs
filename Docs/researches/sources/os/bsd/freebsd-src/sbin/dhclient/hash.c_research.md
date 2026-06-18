# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/hash.c

## Purpose
Implements a small chained hash table used for DHCP option/universe name lookup.

## Main Elements
- `new_hash()`: allocates a default-size hash table and clears buckets.
- `do_hash()`: byte-sum hash with carry folding modulo table size.
- `add_hash()`: allocates a bucket, stores name pointer, length, value pointer, and prepends to bucket chain.
- `hash_lookup()`: searches a bucket by length and byte comparison.

## Dependencies And Integration
Uses allocation wrappers declared in `dhcpd.h` and warnings from `errwarn.c`. `tables.c` uses it to index DHCP option names and universes for config parsing.

## Risk Notes
Names are not copied, only referenced, so callers must provide stable storage. Hash quality is simple but sufficient for small static option tables.
