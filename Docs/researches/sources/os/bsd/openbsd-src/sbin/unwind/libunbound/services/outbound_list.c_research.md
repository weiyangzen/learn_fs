# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.c

## Role

Implements a small doubly linked list used by modules to track outbound serviced queries currently outstanding to authoritative/upstream servers.

## Functions

- `outbound_list_init`: initializes an empty list by setting `first = NULL`.
- `outbound_list_clear`: walks all entries, stops each serviced query through `outnet_serviced_query_stop(p->qsent, p)`, then reinitializes the list.
- `outbound_list_insert`: inserts an entry at the head and fixes `prev` links.
- `outbound_list_remove`: stops the associated serviced query, unlinks the entry from the list, and leaves memory reclamation to the owning region/lifetime.

## Dependencies

- Includes `services/outside_network.h` for `outnet_serviced_query_stop`.
- The list entries connect outbound network service state back to the `module_qstate` that issued them.

## Research Notes

- The implementation comments say entries are region allocated, so removal does not free memory.
- `outbound_list_remove` tolerates `NULL` entries.
