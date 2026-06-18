# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.h

`pfctl_parser.h` is the main shared declaration header for parser/runtime state, parser-created intermediate nodes, optimizer containers, queue specification trees, option flags, and cross-module prototypes used by `pfctl`.

Primary responsibilities:
- Defines option bit flags such as enable/disable, verbose/no-action/quiet/debug/show-all/optimize/no-DNS/recurse/port-names/ignore-fail/call-show.
- Defines parser constants including `PF_OSFP_FILE`, NAT proxy port range, optimizer modes, and counter-name override macro `FCNT_NAMES`.
- Defines `struct pfctl`, the central runtime/parser state containing device fd, options, optimization mode, anchor stack, transaction buffer, active anchor, queued table state, ruleset name, limiter trees, and pending `set` option values plus set flags.
- Defines parser AST/intermediate structs: `node_if`, `node_host`, `node_os`, queue bandwidth/HFSC option nodes, table initializer nodes, optimizer table/rule wrappers, queue spec tree items, and syncookie watermarks.
- Declares RBT heads for state/source limiter lookup by id/name.
- Declares parser, loader, optimizer, table, queue, print, address, OS fingerprint, ICMP, loglevel, and transaction helper functions.

Important structures:
- `struct pfctl` binds parser actions to eventual kernel load, including anchor stack depth, current anchor, transaction buffer, limit/timeout/debug/logif/hostid/reassembly/syncookie settings, and RBT limiter registries.
- `struct node_host` is the parser’s normalized address/interface host node, with address wrap, broadcast/peer fields, AF, negation, link-local index, load-balancing weight, interface name, and list/tail pointers.
- `struct pf_opt_tbl` and `struct pf_opt_rule` are optimizer containers that extend PF kernel objects with generated table refs, profile counts, and queue entries.
- `struct pfctl_qsitem` forms queue definition trees for validation/loading.

Integration points:
- Included by `pfctl.c`, `pfctl_parser.c`, `pfctl_optimize.c`, `pfctl_osfp.c`, `pfctl_queue.c`, and likely grammar-generated parser sources in the same directory.
- Complements `pfctl.h`: `pfctl.h` owns table-buffer and command-facing declarations; this header owns parser/runtime state and parser support declarations.
- Uses kernel PF structures heavily, so field layout and constants track `<net/pfvar.h>`.

Notable risks and edge cases:
- `PFCTL_ANCHOR_STACK_DEPTH` is fixed at 64 for parser anchor nesting.
- The option bitmask is shared by CLI, parser, and output code; new flags must avoid collisions.
- Many prototypes expose mutable raw kernel structs, reflecting the C codebase’s direct ABI-oriented style rather than encapsulation.
