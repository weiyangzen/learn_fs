# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.c

This file implements the `isakmpd` configuration database, parser, transactions, defaults, and reporting.

Key responsibilities:
- Parses INI-like configuration files with `[section]` headers and `tag=value` assignments.
- Stores configuration bindings in a 256-bucket hash table keyed by section.
- Supports transactional changes with queued set/remove/remove-section operations.
- Loads and applies a large matrix of default phase 1 and phase 2 configuration sections.
- Provides typed accessors for strings, numbers, socket addresses, numeric ranges, comma-separated lists, and section tag lists.
- Handles SIGHUP-style reinitialization by replacing current configuration.
- Dumps non-default running configuration for reports.

Important structures:
- `struct conf_binding`: committed config entry with section, tag, value, and default flag.
- `struct conf_trans`: queued transaction operation.
- `struct conf_list` and `struct conf_list_node`: list return types declared in `conf.h`.

Important functions:
- `conf_init()` initializes hash buckets and the transaction queue, then calls `conf_reinit`.
- `conf_reinit()` opens the config through monitor helpers, checks secrecy, reads it, parses it, loads defaults, and commits.
- `conf_parse()` and `conf_parse_line()` implement file parsing.
- `conf_load_defaults()` creates default general, X.509, KeyNote, lifetime, phase 1, main-mode transform, and quick-mode suite sections.
- `conf_load_defaults_mm()` and `conf_load_defaults_qm()` generate individual main-mode and quick-mode defaults.
- `conf_get_str()`, `conf_get_num()`, `conf_get_address()`, `conf_match_num()`, `conf_get_list()`, and `conf_get_tag_list()` are accessors.
- `conf_begin()`, `conf_set()`, `conf_remove()`, `conf_remove_section()`, and `conf_end()` implement transactions.
- `conf_report()` emits non-default configuration entries.

Notable behavior:
- Duplicate tags are ignored unless override is requested.
- Defaults are marked with `is_default` so reports can omit them.
- Config file absence is tolerated; defaults are still loaded.
- Default generation covers many combinations of encryption, hash, authentication method, DH group, protocol, tunnel/transport mode, and PFS.
- AH defaults reject encryption; ESP defaults reject missing encryption; GCM/GMAC reject separate authentication in quick-mode default generation.
- Escaped newlines are folded into spaces during parse.

Dependencies:
- Uses monitor file-open and secrecy-check helpers.
- Uses `text2sockaddr` from utility code for address parsing.
- Uses `log` for diagnostics.
- Depends on constants from `conf.h`.

Research notes:
- This is the central configuration service for many `isakmpd` modules.
- The default matrix is extensive and provides implicit named sections even when the config file is small or absent.
