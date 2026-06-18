# sources/sync-backup/bup/test/int/test_shquote.py

Purpose: validates shell-like byte command-line splitting and completion quoting helpers in `bup.shquote`.

Important APIs/types/functions: `shquote.quotesplit`, `shquote.unfinished_word`, `shquote.what_to_add`, `shquote.quotify_list`, and local `qst()` to strip offsets.

Control flow: tests split whitespace, backslash-escaped quotes, single/double quotes, unfinished quotes, and adjacent quoted/unquoted segments. Completion tests derive the unfinished word and quote type, then ask what suffix to add for unquoted, single-quoted, double-quoted, and escaped words. Final assertion checks list quoting for empty strings, embedded quotes, lone quote, and spaces.

State and persistence behavior: pure byte-string parsing with no external state.

Dependencies/integration points: supports bup shell completion and user-facing command rendering. It overlaps with but is distinct from `bup.io` shell escaping because it parses/edit-completes partially typed command lines.

Risks and test signals: behavior is exact and shell-dialect-specific. Signals are offset-preserving split tuples, unfinished quote markers, completion suffixes including closing quotes when requested, and a canonical quoted list.
