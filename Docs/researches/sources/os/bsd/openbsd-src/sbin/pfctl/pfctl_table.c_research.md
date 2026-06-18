# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_table.c

## Purpose

Implements `pfctl` table and interface subcommands for OpenBSD PF. This file is the userland control surface around `pfr_*` and `pfi_*` kernel ioctls: listing, creating, deleting, flushing, replacing, expiring, testing, and zeroing PF tables and table address counters.

## Main Entry Points

- `pfctl_clear_tables()` and `pfctl_show_tables()` are small wrappers around `pfctl_table()` for `-F` and `-s`.
- `pfctl_table()` dispatches string commands such as `-F`, `-s`, `kill`, `flush`, `add`, `delete`, `replace`, `expire`, `show`, `test`, and `zero`.
- `pfctl_define_table()` defines parser-created tables, either directly through `pfr_ina_define()` for root/command tables or by filling a `pfr_uktable` for later non-root anchor loading.
- `pfctl_show_ifaces()` and `print_iface()` list PF interface accounting.

## Control Flow And Behavior

`pfctl_table()` initializes a `pfr_table`, copies the optional table name and anchor with bounds checks, sets `PFR_FLAG_DUMMY` for no-action mode, then uses command-specific pfr operations. Dynamic result retrieval uses grow-and-retry loops: allocate/grow a `pfr_buffer`, set `pfrb_size` to current capacity, call `pfr_get_tables()`, `pfr_get_tstats()`, `pfr_get_addrs()`, `pfr_get_astats()`, or `pfi_get_ifaces()`, and repeat until returned size fits.

Address-changing commands load argv and optional file input with `load_addr()`, which calls `append_addr()` for each argument and `pfr_buf_load()` for files. `add` and `replace` use `CREATE_TABLE`, which warns about duplicate active table names in other anchors, temporarily sets `PFR_TFLAG_PERSIST`, and calls `pfr_add_tables()` unless in syntax-only mode. Verbose operations set `PFR_FLAG_FEEDBACK` and print only changed feedback entries unless very verbose output is requested.

`expire` reads address stats, compares `time(NULL) - pfras_tzero` against a parsed lifetime, builds a second buffer of stale addresses, and deletes them. `test` optionally clones the input address buffer under `PF_OPT_VERBOSE2` so the original query address and returned match address can be printed side by side. `zero` either clears selected address counters or clears table and address stats together with `PFR_FLAG_ADDRSTOO`.

## Output And Formatting

`print_table()` emits compact flag columns for const, persist, active, inactive, referenced, referenced-anchor, and counters. `print_tstats()` and `print_astats()` format clear times, references, evaluations, packets, bytes, active states, weights, and interface names. `print_addrx()` prints PF address feedback markers, negation, CIDR prefix, optional matched address, optional reverse DNS for host addresses, and optional interface suffix.

## Dependencies And State

The file depends on PF userland/kernel APIs from `net/pfvar.h`, shared parser/helper declarations in `pfctl_parser.h` and `pfctl.h`, and buffer helpers such as `pfr_buf_grow()`, `pfr_buf_add()`, `pfr_buf_clear()`, `PFRB_FOREACH`, `append_addr()`, and `pfr_buf_load()`.

## Risks And Invariants

- Table and anchor names must fit `PF_TABLE_NAME_SIZE` and destination buffers; overlong names trigger usage or fatal errors.
- `RVTEST` intentionally suppresses real kernel calls in syntax-only mode unless dummy action is requested; command behavior depends on this macro.
- Buffer grow loops rely on kernel APIs returning the needed element count through `pfrb_size`.
- `print_addrx()` computes `hostnet` from the printed address family; when printing a matched address (`rad`) it assumes compatible family/prefix semantics.
- `pfctl_define_table()` transfers ownership of address buffers into `pfr_uktable` by clearing the source buffer fields after assignment.
