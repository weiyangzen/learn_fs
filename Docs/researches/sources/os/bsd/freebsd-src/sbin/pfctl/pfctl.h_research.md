# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.h

## Purpose

`pfctl.h` is the shared local header for the pfctl userland modules. It declares common structs, macros, globals, and cross-file functions used by rule loading, parsing, tables, ALTQ, state display, and OS fingerprint support.

## Main Contents

The header includes `<libpfctl.h>` and exposes the global PF handle:

- `extern struct pfctl_handle *pfh;`

It defines:
- `DBGPRINT(...)`: conditional debug printing under `PFCTL_DEBUG`.
- `enum pfctl_show`: output mode for rules, labels, or no output.
- `struct pfr_buffer`: local growable buffer abstraction used for tables, addresses, interface lists, transactions, and stats.
- `PFRB_FOREACH`: iterator over `pfr_buffer`.
- `struct pfr_ktable` and `struct pfr_uktable`: pfctl-side table representations used while parsing/loading table state.
- `struct pfr_anchoritem` and `SLIST_HEAD(pfr_anchors, ...)`: anchor-list representation for recursive operations.
- `struct segment`: service-curve segment used by ALTQ admission control.

## Buffer And Table Interfaces

The header declares table and address buffer functions:
- `pfr_add_table`, `pfr_del_table`, `pfr_get_tables`
- `pfr_clr_astats`, `pfr_clr_addrs`
- `pfr_add_addrs`, `pfr_del_addrs`, `pfr_set_addrs`
- `pfr_get_addrs`, `pfr_get_astats`, `pfr_tst_addrs`
- `pfr_ina_define`
- `pfr_buf_clear`, `pfr_buf_add`, `pfr_buf_next`, `pfr_buf_grow`, `pfr_buf_load`

These support parser-driven table definitions and runtime table commands.

## pfctl Cross-Module Declarations

The header declares shared front-end functions:
- table operations: `pfctl_do_clear_tables`, `pfctl_show_tables`, `pfctl_table`
- ALTQ display: `pfctl_show_altq`
- interface display: `pfctl_show_ifaces`
- creator ID display: `pfctl_show_creators`
- safe file open: `pfctl_fopen`
- title printing: `pfctl_print_title`
- parse macro definition: `pfctl_cmdline_symset`

It also declares print helpers used by multiple files:
- `print_addr`
- `print_addr_str`
- `print_host`
- `print_seq`
- `print_state`

## Transaction And Ruleset Interfaces

Important rule-loading declarations:
- `pfctl_add_trans`
- `pfctl_get_ticket`
- `pfctl_trans`
- `pf_get_ruleset_number`
- `pf_init_ruleset`
- `pfctl_anchor_setup`
- `pf_remove_if_empty_ruleset`
- `pf_find_ruleset`
- `pf_find_or_create_ruleset`
- `pf_init_eth_ruleset`
- `pfctl_eth_anchor_setup`
- `pf_find_or_create_eth_ruleset`
- `pf_remove_if_empty_eth_ruleset`
- `expand_label`

These are the glue between parser output, anchor/ruleset trees, and kernel transactions.

## FreeBSD-Specific Definitions

Under `__FreeBSD__`, the header exposes:
- `extern int altqsupport;`
- `extern int dummynetsupport;`
- `HTONL(x)` macro wrapping `htonl`.

It also supplies default queue constants if not already defined:
- `DEFAULT_PRIORITY`
- `DEFAULT_QLIMIT`

## ALTQ Declarations

ALTQ-related declarations include:
- `check_commit_altq()`
- `pfaltq_store()`
- `rate2str()`

The `struct segment` definition supports generalized service-curve math in `pfctl_altq.c`.

## Error And Protocol Helpers

Declared shared helpers:
- `pfctl_proto2name()`
- `pfctl_err()`
- `pfctl_errx()`
- `pf_strerror()`

## Role In This Group

This header is a coordination point rather than a behavior-heavy module. It defines the local ABI between pfctl’s parser, table manager, queueing support, optimizer, display code, and main command dispatcher.
