# sources/storage-engines/wiredtiger/src/config/config.c

## Purpose
This file is the generic WiredTiger configuration string scanner and lookup engine. It parses key/value strings, nested structures, quoted strings, booleans, integers with size suffixes, and priority-ordered arrays of configuration strings.

## Important APIs, Types, and Functions
`__wti_config_parse_dec` is a bounded `strtoll`-style decimal parser. `__wt_config_initn`, `__wt_config_init`, and `__wt_config_subinit` initialize `WT_CONFIG` parsers. `__wt_config_next` returns processed key/value pairs. Lookup APIs include `__wti_config_get`, `__wt_config_gets`, `__wt_config_getone`, `__wt_config_getones`, `__wt_config_getones_n`, `__wt_config_gets_def`, `__wt_config_subgetraw`, `__wt_config_subgets`, and `__wt_config_subget_next`. Internal helpers include `__config_next`, `__config_getraw`, and `__config_process_value`.

## Control Flow
The scanner uses table-driven actions (`gostruct`, `gobare`, `gostring`, `goutf8_continue`, and `goesc`) instead of ad hoc token parsing. `__config_next` tracks bracket depth, top-level item boundaries, quote state, escapes, UTF-8 continuation bytes, separators, and implicit `true` values for keys without explicit values. `__config_process_value` converts `true` and `false` IDs to booleans, parses decimal integers, and applies `b/k/m/g/t/p` suffix shifts when safe. `__config_getraw` scans a parser for the last matching key, recurses through dotted nested keys, and processes the final value at the top level. `__wti_config_get` searches config string arrays in reverse so later user configs override defaults.

## State and Persistence
Parser state is held in `WT_CONFIG`: original string, current pointer, end pointer, depth, top marker, and active transition table. The module does not persist data, but it is the canonical interpreter for configuration strings stored in metadata and supplied to public APIs. Its parsing choices therefore influence object creation, recovery, checkpoints, cursors, transactions, and connection settings.

## Dependencies and Integration Points
It depends on WiredTiger character classification helpers, error macros, `WT_CONFIG_ITEM`, and `WT_CONFIG` definitions from `config.h`. It feeds validation in `config_check.c`, compiled configuration in `conf_compile.c`, public config parser APIs in `config_api.c`, schema parsing, metadata checkpoint parsing, cursor options, connection reconfiguration, transaction options, and many performance-sensitive defaults via `__wt_config_gets_def`.

## Risks and Edge Cases
The finite-state tables are compact but hard to audit; a single table entry can change accepted syntax. Numeric parsing must handle overflow, negative values, suffix shifts, and partial parses correctly. Quoted strings accept only valid UTF-8 sequences and limited escapes. Nested dotted lookup returns the final matching value, so duplicate keys and override order are intentional. `__wt_config_gets_def` makes assumptions about common two-string config arrays for performance.

## Test Signals
Parser unit and csuite config tests are essential, including malformed brackets, unbalanced quotes, escapes, UTF-8, duplicate keys, nested structures, boolean shorthand, numeric suffixes, overflow, `none` handling, and reverse override order. Broader schema, cursor, checkpoint, metadata, and transaction tests provide integration coverage because they all consume this parser.
