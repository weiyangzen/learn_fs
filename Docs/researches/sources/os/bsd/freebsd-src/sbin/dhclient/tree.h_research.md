# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tree.h

## Purpose
Defines small parse-tree/list and DHCP option metadata structures.

## Main Elements
- `pair`: cons-cell style linked list node with `car` and `cdr`.
- `struct tree_cache`: option value pointer, length, buffer size, and timeout metadata used during option assembly.
- `struct universe`: named option namespace with hash table and option pointer array.
- `struct option`: option name, format string, owning universe, and code.

## Dependencies And Integration
Included by `dhcpd.h`; consumed by parser, option tables, hash lookup, and option assembly.

## Risk Notes
These are lightweight shared structs with no ownership semantics encoded. Callers must keep referenced option values and names valid.
