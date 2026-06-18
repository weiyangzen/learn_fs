# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/alloc.c

## Purpose
Provides small allocation helpers for DHCP client data structures.

## Main Elements
- `new_string_list(size)`: allocates a `struct string_list` plus inline string storage and points `string` into the tail.
- `new_hash_table(count)`: allocates a hash table sized for `count` buckets and records `hash_count`.
- `new_hash_bucket()`: allocates a zeroed hash bucket.

## Dependencies And Integration
Included through `dhcpd.h`. Used by parser and option/hash table code.

## Risk Notes
These helpers return `NULL` on allocation failure; most callers treat allocation failure as fatal.
