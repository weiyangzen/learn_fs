# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/oed.c

Implements the `dict` backend for the Oxford English Dictionary 2nd Edition. It translates OED SGML-like tags and entity names into Plan 9/Unicode output through the common `dict.h` callback contract: `oedprintentry`, `oednextoff`, and `oedprintkey`.

The file is mostly format tables and a parser. `tagtab` maps OED tags such as `hw`, `s1`, `etym`, `pr`, `gk`, `ph`, and quote/sense tags to internal enum values. `auxtab` parses tag attributes including sense number and status. `spectab` maps hundreds of entity names to Unicode runes, private ligature codes, or multi-rune expansions shared through `utils.c`.

`oedprintentry` walks the entry bytes with a current translation table. Normal text is emitted through `outrune`; special-character starts are parsed by `getspec`; tags are parsed by `gettag`. It switches translation tables for phonetic, Greek, superscript, and subscript regions via `changett`, delays one rune to combine accents with the previous rune through `liglookup`, expands multi-rune entities through `multitab`, and uses `outinhibit` to print only headwords for `cmd == 'h'`.

Entry layout behavior is tag-driven. Main entries and variant entries start new output lines; etymology/editor tags add brackets; pronunciation tags add parentheses; sense tags add indentation and labels from `num=`; paragraph/quote/table tags affect line breaks; `st=` statuses are rendered by `dostatus` as dagger/parallel/paragraph markers where recognized. Unknown tags/entities/statuses are debug-only diagnostics except unknown entities become replacement characters.

`oednextoff` scans `bdict` for the next `<e...>` or `<ve...>` start tag and returns the byte offset for the next entry. `oedprintkey` prints a built-in pronunciation key string.

Integration points: registered in `utils.c` as dictionary name `oed`, using `/lib/dict/oed2` and `/lib/dict/oed2index`. It depends on common output wrapping, binary-search association lookup, ligature handling, and global debug/output state in `utils.c`.

Risks and notes: the parser is permissive and fixed-buffer based (`Buflen`, `Maxaux`), so malformed long tags or many attributes truncate silently. Many special symbols are approximate, with comments noting missing exact Unicode equivalents. The tag parser assumes simple unquoted `name=value` attributes.
