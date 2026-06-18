# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.h

`pfctl.h` is the shared public header for non-parser `pfctl` modules. It defines shared table-buffer infrastructure, anchor-list structures, user-kernel table wrappers, display mode enums, and cross-file prototypes for PF table, interface, state, queue, error, printing, and transaction helpers.

Primary responsibilities:
- Defines `DBGPRINT()` as a compile-time optional debug macro under `PFCTL_DEBUG`.
- Defines `enum pfctl_show` for rule/label/no-output display formats.
- Defines `PFRB_*` buffer types and `struct pfr_buffer`, a typed dynamic array used for tables, table stats, addresses, address stats, interfaces, and transaction entries.
- Provides `PFRB_FOREACH()` iteration over typed buffers via `pfr_buf_next()`.
- Defines `struct pfr_anchoritem` and `SLIST_HEAD(pfr_anchors, ...)` for recursive anchor traversal.
- Defines `struct pfr_uktable`, the userland table wrapper that embeds a kernel table plus initializer address buffer and list linkage.
- Exposes `pfr_ktables`, the global RB tree of parser-created table definitions.

Important exported APIs:
- Table operations: `pfr_clr_tables()`, `pfr_add_tables()`, `pfr_del_tables()`, `pfr_get_tables()`, `pfr_get_tstats()`, `pfr_clr_tstats()`, `pfr_*_addrs()`, `pfr_tst_addrs()`, and `pfr_ina_define()`.
- Buffer operations: `pfr_buf_clear()`, `pfr_buf_add()`, `pfr_buf_next()`, `pfr_buf_grow()`, and `pfr_buf_load()`.
- User-visible command helpers: `pfctl_clear_tables()`, `pfctl_show_tables()`, `pfctl_table()`, `pfctl_show_ifaces()`, and `pfctl_show_queues()`.
- Printing helpers shared across modules: address, host, sequence, state, title, and error functions.
- Transaction helpers: `pfctl_add_trans()`, `pfctl_get_ticket()`, and `pfctl_trans()`.
- Limiter name resolution: `pfctl_statelim_id2name()` and `pfctl_sourcelim_id2name()`.

Integration points:
- Implemented primarily by `pfctl_radix.c`, `pfctl.c`, `pfctl_parser.c`, `pfctl_queue.c`, and table/interface modules elsewhere in the pfctl directory.
- Includes forward declaration for `struct pfctl` because detailed parser/runtime state lives in `pfctl_parser.h`.
- Mirrors kernel PF structures from `<net/pfvar.h>` but keeps userland buffer and wrapper abstractions local to `pfctl`.

Notable risks and edge cases:
- `struct pfr_buffer` correctness depends on `pfrb_type`; the implementation maps each type to a fixed element size.
- The `pfr_uktable` field-alias macros expose embedded kernel table fields, which keeps parser code terse but couples field layout to `struct pfr_ktable`.
- This header is central shared ABI within `pfctl`; changes here affect several C files.
