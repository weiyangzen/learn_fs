# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.c

`pfctl.c` is the main command implementation for OpenBSD `pfctl`. It owns CLI option parsing, `/dev/pf` access mode selection, high-level command dispatch, PF enable/disable/reset paths, rule loading transactions, anchor recursion, state/source-node operations, queue loading, state/source limiter loading, and display flows for rules, labels, state, sources, status, limits, timeouts, tables, queues, interfaces, and OS fingerprints.

Primary responsibilities:
- Defines global command state such as selected clear/show/table/debug options, PF device path, interface/table/anchor selectors, kill keys, `dev`, title formatting state, label state, and final `exit_val`.
- Implements fatal/nonfatal wrappers `pfctl_err()` and `pfctl_errx()` that honor `PF_OPT_IGNFAIL` for recursive best-effort operations.
- Implements direct PF controls through ioctls including `DIOCSTART`, `DIOCSTOP`, `DIOCCLRSTATUS`, `DIOCCLRIFFLAG`, `DIOCCLRSTATES`, `DIOCCLRSRCNODES`, `DIOCKILLSTATES`, `DIOCKILLSRCNODES`, `DIOCGETSTATUS`, `DIOCGETSYNFLWATS`, `DIOCGETTIMEOUT`, `DIOCGETLIMIT`, and option-setting ioctls.
- Drives rule loading through `pfctl_rules()`, which initializes parser state, creates ruleset/table transactions, parses config with `parse_config()`, validates queue assignments, loads queues/state limiters/source limiters/options, recursively loads anchors/rules/tables, and commits or rolls back transactions.
- Handles anchor traversal and recursive clear/show operations through `pfctl_walk_anchors()`, `pfctl_get_anchors()`, and `pfctl_recurse()`.
- Maintains local RBT caches for state limiter and source limiter lookup by id/name so rule printing can resolve limiter names on demand.

Important control flow:
- `main()` parses flags with `getopt()`, validates mutually exclusive DNS modes and table command pairing, normalizes anchor wildcard syntax, opens `/dev/pf` unless `-n` no-action prevents mutation, reads current PF limits, and then dispatches show, clear, kill, table, rule-load, enable, debug, state-store, and state-load operations.
- No-action mode clears mutating flags and may still open `/dev/pf` read-only to populate current limits for realistic parse/load simulation.
- Rule loading uses transaction buffers from `pfctl_add_trans()`/`pfctl_get_ticket()`/`pfctl_trans()`. Main ruleset loading begins transactions before parsing because table definitions are still loaded at parse time.
- `pfctl_load_ruleset()` recurses over in-memory parser-created `pf_ruleset` trees, optionally optimizes a ruleset, expands labels, calls `pfctl_load_rule()`, descends into child anchors, and finally loads tables scoped to each anchor.
- Queue definitions are collected in global `qspecs` and `rootqs`; `pfctl_check_qassignments()` builds hierarchy and enforces leaf assignment before `pfctl_load_queues()` sends them with `DIOCADDQUEUE`.

Integration points:
- Depends on parser state and helpers from `pfctl_parser.h`/`pfctl_parser.c`, including `parse_config()`, `print_rule()`, host/address helpers, table buffers, limiter structs, queue structs, and option setters.
- Depends on table/radix wrappers from `pfctl_radix.c` for table transactions and table buffer handling.
- Calls OS fingerprint functions from `pfctl_osfp.c` when showing/loading rules or loading the main ruleset.
- Calls queue display from `pfctl_queue.c`; queue loading itself is in this file.
- Calls optimizer from `pfctl_optimize.c` when optimization is enabled.
- Relies heavily on kernel ABI structures from `<net/pfvar.h>` and ioctls against `/dev/pf`.

Data and state:
- `limit_curr[]` snapshots current PF limits so temporary load failures can restore settings via `pfctl_restore_limits()`.
- `pfctl_init_options()` fills parser/runtime defaults for timeouts, limits, syncookie watermarks, debug level, and reassembly. Fragment/table limits are derived partly from `sysctl()` values and current kernel limits.
- State and source limiter caches are RBTs embedded in `struct pfctl`.

Notable risks and edge cases:
- The file is process-oriented: many allocations are intentionally not freed on success because `pfctl` exits shortly after command completion.
- Recursive anchor modification sets `PF_OPT_IGNFAIL`, so failures in one anchor do not abort cleanup of later anchors; callers must rely on accumulated return value.
- String copying consistently uses `strlcpy()`/fixed-size kernel ABI fields, with explicit fatal errors on overflow.
- State/source kill paths resolve hostnames unless `PF_OPT_NODNS` is set and deduplicate only adjacent `getaddrinfo()` duplicates.
- `pfctl_key_kill_states()` requires an exact four-token key format: protocol, host:port, direction, host:port.
- Anchor names beginning with `_` are protected from command-line modification because those anchors are reserved for unnamed brace notation.
