## sources/security-integrity/audit-userspace/src/ausearch-lookup.c

Purpose: converts raw audit values into readable or safely escaped output for `ausearch` and report summaries.

Important APIs/functions: `aulookup_result()`, `aulookup_success()`, `aulookup_syscall()`, `aulookup_uid()`, `aulookup_destroy_uid_list()`, `unescape()`, `safe_print_string_n()`, `safe_print_string()`, and `print_tty_data()`. Internal helpers map `socketcall`/`ipc` subcalls, hex-decode strings, escape TTY/shell output, and name TTY control sequences.

Control flow: lookup functions lazily initialize an `auparse` buffer parser for interpretations. UID lookups prefer enriched interpretations, then cache `getpwuid()` results in an `nvlist`. `safe_print_string_n()` chooses escaping based on global `escape_mode`. `print_tty_data()` decodes hex TTY data into printable text and named keys.

State/persistence: static `interp_init`, `au`, `machine`, UID cache, and constant lookup tables. No persistence; cache is destroyed by explicit cleanup.

Dependencies/integration: uses `libaudit`, `ausearch-options` report/escape globals, `ausearch-nvpair`, `auparse-idata`, Linux socket constants, and generated `auparse/tty_named_keys.h`.

Risks/test signals: lazy static parser and UID cache are not thread-safe. `unescape()` accepts both parenthesized and hex strings and returns malloced data that callers own. Output escaping is security-sensitive. Tests should include shell metacharacters, control bytes, malformed hex, abstract UNIX sockets, unknown uids, enriched interpretations, and TTY named key sequences.
