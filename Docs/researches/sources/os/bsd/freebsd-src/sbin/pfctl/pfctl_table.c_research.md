# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_table.c

## Purpose
Implements pfctl table and interface commands: list, create, delete, flush, add, replace, expire, reset, show, test, zero, and interface display.

## Main Elements
- `pfctl_table()` dispatches table commands and manages `pfr_buffer` instances for addresses, stats, and tables.
- Creates persistent tables when needed and warns on duplicate table names in other anchors.
- Loads addresses from argv or files and prints feedback markers for add/delete/replace/test/zero operations.
- Prints table stats, address stats, DNS-resolved address output, and interface stats.
- `pfctl_define_table()` handles parse-time table definitions and inactive table loading.

## Dependencies And Integration
Uses wrappers from `pfctl_radix.c`, libpfctl table APIs, shared parser address expansion, `usage()`, and PF table/interface ABI structures.

## Risk Notes
`PF_OPT_NOACTION`, dummy action, recursion, and feedback flags alter behavior. Table commands are stateful kernel mutations, so error and cleanup paths matter.
