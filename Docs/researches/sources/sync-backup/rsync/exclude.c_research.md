# sources/sync-backup/rsync/exclude.c

## Purpose
Implements rsync include/exclude/filter rule parsing, matching, transmission, daemon filters, CVS ignores, implied includes from transfer args, per-directory merge files, and local filter stack management.

## Important APIs, Types, and Functions
Global lists are `filter_list`, `cvs_filter_list`, `daemon_filter_list`, and `implied_filter_list`. Public functions include `add_implied_include()`, `implied_include_partial_string()`, `free_implied_include_partial_string()`, `set_filter_dir()`, `push_local_filters()`, `pop_local_filters()`, `change_local_filter_dir()`, `name_is_excluded()`, `check_server_filter()`, `check_filter()`, `rule_template()`, `parse_filter_str()`, `parse_filter_file()`, `get_rule_prefix()`, `send_filter_list()`, and `recv_filter_list()`. Static helpers parse rule tokens, build rules, manage merge-list lifetimes, match wildcard/literal patterns, and report debug decisions.

## Control Flow
Filter setup parses command-line, daemon, CVS, and merge-file rules into linked lists. `add_rule()` normalizes directory suffixes, absolute paths, wildcards, side-specific flags, and per-dir merge list objects. During traversal, `push_local_filters()` updates `dirbuf`, saves inherited merge-list state, loads merge files in the current directory, and `pop_local_filters()` restores previous state. Matching walks daemon filters first, then transfer filters, recursively checking per-dir merge lists and CVS lists. Client/server filter exchange serializes compatible prefixes and elides local-only rules depending on sender/receiver side and protocol.

## State and Persistence Behavior
Maintains process-global linked lists, per-directory inherited filter state, `dirbuf`, `dirbuf_depth`, merge-list parent arrays, `cur_elide_value`, `saw_xattr_filter`, `trust_sender_args`, and `trust_sender_filter`. It reads filter files, `.cvsignore`, `$HOME/.cvsignore`, and `CVSIGNORE`, but does not write persistent files.

## Dependencies and Integration Points
Depends on wildcard matching, path sanitization, current directory/module globals, daemon config (`lp_use_chroot()`), protocol version, IO serialization, logging, and file-list/delete/generator code. `delete.c` uses local filters to decide deletability, and `clientserver.c` builds `daemon_filter_list` from module config.

## Risks and Test Signals
Risks include side-specific rule elision mistakes, daemon filter bypass, unsafe merge-file path handling under sanitized paths, inherited per-dir list lifetime bugs, protocol-incompatible rule prefixes, xattr filter mismatches, and implied-include validation holes. Test signals include command-line include/exclude combinations, `--delete-excluded`, sender/receiver-side hide/protect/risk/show rules, per-dir merge files with no-inherit/exclude-self/CVS modes, daemon filters, sanitized module paths, xattr filters, old protocol filter exchange, and implied include validation for wildcards and relative paths.
