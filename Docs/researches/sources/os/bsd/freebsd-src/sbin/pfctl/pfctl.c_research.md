# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.c

## Purpose

`pfctl.c` is the main userland control program for FreeBSD PF. It parses `pfctl` command-line options, opens the PF device/netlink handle, dispatches show/flush/load/kill operations, and coordinates parser output with kernel/libpfctl transactions.

It is the central integration file for:
- Enabling/disabling PF and ALTQ.
- Loading rules, NAT, Ethernet rules, tables, ALTQ, options, state limiters, and source limiters.
- Showing status, rules, anchors, tables, states, source nodes, timeouts, limits, OS fingerprints, creator IDs, and queue state.
- Flushing rules/NAT/tables/states/statistics/source nodes/fingerprints/options.
- Killing PF states or source tracking entries by network, gateway, label, ID, key, source limiter entry, or interface.
- Managing anchor recursion and rule transaction lifecycles.

## Main Data And Globals

Key globals:
- `dev`: opened PF device descriptor.
- `pfh`: global `struct pfctl_handle *` used by libpfctl calls.
- `loadopt`: bitmask of requested load categories such as NAT/filter/table/option/ALTQ/Ethernet.
- `altqsupport`: runtime ALTQ availability flag.
- `pf_main_anchor`, `pf_eth_main_anchor`, `pf_anchors`: parser/load anchor state.
- `skip_b`: cached interface list used when preserving or adjusting `set skip` interface flags.
- command option globals such as `clearopt`, `rulesopt`, `showopt`, `debugopt`, `anchoropt`, `ifaceopt`, `tableopt`, `tblcmdopt`, and kill argument arrays.

The file uses FreeBSD PF structs from `<net/pfvar.h>`, parser-owned structs from `pfctl_parser.h`, and shared declarations from `pfctl.h`.

## CLI Dispatch

`main()` parses the `pfctl` CLI:
- `-e` / `-d`: enable or disable PF.
- `-f`: load rules from file.
- `-F`: flush selected data.
- `-s`: show selected data.
- `-T` / `-t`: table command and table name.
- `-k`: kill states, with special modes `label`, `id`, `gateway`, `key`, and `source`.
- `-K`: kill source nodes.
- `-a`: operate on an anchor, with trailing `*` enabling recursion.
- `-o`: select optimizer level: `none`, `basic`, or `profile`.
- `-n`: no-action parse/check mode.
- `-m`: merge mode.
- `-M`: kill matching states.
- `-S` and `-r`: DNS resolution behavior.

After option parsing, `main()` opens PF, tests ALTQ support, reads current limits, dispatches show/flush/kill/table/load/debug/enable operations, and closes `dev`/`pfh` on successful exit to avoid the registered limit restore handler.

## Error Handling

`pfctl_err()` and `pfctl_errx()` wrap `err`/`errx` behavior with `PF_OPT_IGNFAIL` support. In ignore-failure mode, they warn, set `exit_val`, and let recursive clearing continue where possible.

`pf_strerror()` maps selected PF errors to user-facing anchor/table messages.

## Protocol Name Cache

`pfctl_proto2name()` caches protocol number to name translations for protocol IDs up to 258, avoiding repeated `getprotobynumber()` calls during large state dumps. It duplicates names because libc protocol lookup storage may be overwritten on subsequent calls.

## Enable, Disable, And Status Clearing

- `pfctl_enable()` calls `pfctl_startstop(pfh, 1)`, reports common errors, optionally starts ALTQ with `DIOCSTARTALTQ`, and prints `pf enabled`.
- `pfctl_disable()` calls `pfctl_startstop(pfh, 0)`, optionally stops ALTQ with `DIOCSTOPALTQ`, and prints `pf disabled`.
- `pfctl_clear_stats()` clears PF status counters through `pfctl_clear_status()`.

## Interface Skip Flags

The file caches and adjusts interface skip flags around ruleset loads:
- `pfctl_get_skip_ifaces()` grows `skip_b` and fetches interfaces with `pfi_get_ifaces()`.
- `pfctl_check_skip_ifaces()` clears cached skip flags for interfaces referenced by new rules, including group members.
- `pfctl_adjust_skip_ifaces()` reapplies or clears skip flags after parsing options.
- `pfctl_clear_interface_flags()` clears all `PFI_IFLAG_SKIP` flags through `DIOCCLRIFFLAG`.

## Flush Operations

Implemented flush helpers include:
- `pfctl_flush_eth_rules()`: clear Ethernet rules for an anchor.
- `pfctl_flush_rules()`: clear filter rules for an anchor.
- `pfctl_flush_nat()`: clear NAT/RDR/binat rules.
- `pfctl_clear_altq()`: clears ALTQ through a transaction.
- `pfctl_clear_src_nodes()`: `DIOCCLRSRCNODES`.
- `pfctl_clear_iface_states()`: clears states, optionally scoped to interface and `PF_OPT_KILLMATCH`.

`main()` combines these for `-F all`, `-F Reset`, and recursive anchor operations.

## Address And Kill Helpers

`pfctl_addrprefix()` parses host/network strings with optional CIDR suffix and returns `addrinfo` plus a PF mask.

State/source kill paths:
- `pfctl_kill_src_nodes()` kills source nodes by source and optional destination.
- `pfctl_net_kill_states()` kills states by source/destination network, including special `nat` handling.
- `pfctl_gateway_kill_states()` kills states by route gateway.
- `pfctl_label_kill_states()` kills states by rule label.
- `pfctl_id_kill_states()` kills states by state ID and optional creator ID.
- `pfctl_key_kill_states()` parses `protocol host1:port1 direction host2:port2`.
- `pfctl_kill_source()` clears one source limiter entry by limiter ID and address.
- `pfctl_parse_host()` parses host/port strings into `struct pf_rule_addr`.

## Rule Pool Handling

`pfctl_get_pool()` fetches NAT/RDR/route pool addresses for a kernel rule and builds a `TAILQ` of `pfctl_pooladdr`.

`pfctl_move_pool()` moves pool entries between rule structs without copying allocations.

`pfctl_clear_pool()` releases pool entries.

These are used by show and load paths so pool state survives parser/ruleset copying.

## Showing Rules And Counters

Display helpers include:
- `pfctl_print_eth_rule_counters()`: Ethernet rule evaluation/packet/byte/last-active counters.
- `pfctl_print_rule_counters()`: skip-step debug data, queue IDs, expiration, packet/byte/state/source-node counters, insertion identity, and last-active time.
- `pfctl_print_title()`: section title formatting for `-s all`.

Rule display paths:
- `pfctl_show_eth_rules()`: walks Ethernet rules and wildcard anchors.
- `pfctl_show_rules()`: shows scrub/filter rules, labels, counters, pools, and recursive anchor bodies.
- `pfctl_show_nat()`: shows NAT/RDR/binat rules.
- `pfctl_show_src_nodes()`: prints source tracking nodes.
- `pfctl_show_states()`: fetches states, optionally including rule data for verbose output.
- `pfctl_show_status()`: prints status and syncookie settings.
- `pfctl_show_running()`: reports running state and uses exit status for scripts.
- `pfctl_show_timeouts()` and `pfctl_show_limits()` print current PF timers and limits.
- `pfctl_show_statelims()` and `pfctl_show_sourcelims()` display limiter configuration and counters.
- `pfctl_show_creators()` lists PF state creator IDs.

## Loading Rules

`pfctl_rules()` is the core load operation:
1. Initializes anchor and Ethernet anchor roots.
2. Creates or reuses a transaction buffer.
3. Initializes default PF options.
4. Opens transactions before parsing because tables may be loaded during parse.
5. Calls `parse_config(filename, &pf)`.
6. Adjusts skip interfaces when options are loaded.
7. Loads state/source limiters for the main filter ruleset.
8. Loads scrub, Ethernet, NAT/RDR/binat, and filter rulesets in order.
9. Validates ALTQ with `check_commit_altq()`.
10. Loads nested anchors.
11. Loads global options and commits the transaction, or rolls back on error.

The function respects no-action mode and anchor scoping. ALTQ is disabled for non-root anchors.

## Loading Individual Rules And Rulesets

- `pfctl_init_rule()` initializes a `pfctl_rule` and its pool queues.
- `pfctl_append_rule()` appends parser-produced rules into the current anchor ruleset.
- `pfctl_append_eth_rule()` appends Ethernet rules and creates non-brace anchor structures when needed.
- `pfctl_ruleset_trans()` adds needed rule/table/ALTQ transaction entries before load.
- `pfctl_eth_ruleset_trans()` handles Ethernet-only transactions.
- `pfctl_load_ruleset()` recursively loads anchor rulesets, expands labels/tags, invokes optimization for filter rules, and loads tables tied to anchors.
- `pfctl_load_rule()` begins address pools, loads RDR/NAT/route pools, adds the rule with `pfctl_add_rule_h()`, handles `EEXIST`, prints verbose output, and clears pools.
- `pfctl_load_eth_ruleset()` and `pfctl_load_eth_rule()` perform the same for Ethernet rules.
- `pfctl_add_altq()` adds ALTQ entries and records them for later scheduler validation.

## Options, Defaults, And Reset

`pfctl_init_options()` sets default PF timeout, limit, debug, reassembly, and syncookie values. Some defaults preserve current kernel values when available.

`pfctl_load_options()` applies configured limits, adaptive timeout defaults, all timeouts, debug level, log interface, hostid, reassembly, keepcounters, and syncookies. Merge mode only applies explicitly set fields.

Other option helpers:
- `pfctl_apply_limit()`, `pfctl_load_limit()`
- `pfctl_apply_timeout()`, `pfctl_load_timeout()`
- `pfctl_set_reassembly()`
- `pfctl_set_optimization()`
- `pfctl_set_logif()`, `pfctl_load_logif()`
- `pfctl_set_hostid()`, `pfctl_load_hostid()`
- `pfctl_cfg_syncookies()`, `pfctl_load_syncookies()`
- `pfctl_do_set_debug()`, `pfctl_load_debug()`, `pfctl_debug()`
- `pfctl_set_interface_flags()`

`pfctl_reset()` constructs a default `pfctl` option state, marks all limits/timeouts/options as set, commits them in a transaction, and clears interface skip flags.

## Anchors And Recursion

Anchor functions:
- `pfctl_walk_anchors()` recursively enumerates filter anchors.
- `pfctl_show_anchors()` prints filter anchors.
- `pfctl_show_eth_anchors()` prints Ethernet anchors.
- `pfctl_get_anchors()` builds an SLIST of anchor names, including root.
- `pfctl_recurse()` walks anchor lists for recursive clear/show operations.

Callback wrappers:
- `pfctl_call_cleartables()`
- `pfctl_call_clearrules()`
- `pfctl_call_clearanchors()`
- `pfctl_call_showtables()`

## Limiters

The file defines red-black trees for parsed state and source limiters by ID and name:
- `pfctl_statelim_ids`, `pfctl_statelim_nms`
- `pfctl_sourcelim_ids`, `pfctl_sourcelim_nms`

Load/show functions use `pfctl_state_limiter_*` and `pfctl_source_limiter_*` libpfctl calls.

Notable implementation detail: `pfctl_get_statelim_id()` and `pfctl_get_sourcelim_id()` build an ID key but call `RB_FIND()` on the name tree, which appears inconsistent with their names and the generated ID trees. That should be checked against callers and upstream history before changing, but it is a suspicious local defect.

## External Dependencies

Important functions/types come from:
- `libpfctl`: modern PF accessors such as `pfctl_open`, `pfctl_get_status_h`, `pfctl_add_rule_h`, `pfctl_kill_states_h`, limiter APIs, and state APIs.
- kernel ioctls: `DIOC*` operations for legacy/direct PF controls.
- parser modules: `parse_config`, table routines, anchor setup, print routines, ALTQ validation, fingerprint loading.
- `pfctl_altq.c`, `pfctl_optimize.c`, `pfctl_osfp.c`, and table/parse support files.

## Role In Subset A

This is userland OS/filesystem-adjacent infrastructure rather than filesystem code. In the FreeBSD source tree, it is a high-value OS control-plane example: transaction-oriented kernel configuration loading, stable CLI dispatch, kernel state inspection, recursive namespace/anchor traversal, and conservative semantics-preserving rule transformation.
