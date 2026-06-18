# File Research: sources/os/plan9/9front/sys/src/cmd/mk/word.c

Implements mk word-list creation, parsing, duplication, formatting, and deletion.

Key behavior:
- `newword`, `popword`, `delword`, `wdup`, `wcmp`, and `wadd` manage linked `Word` lists.
- `stow()` parses a string into words, handling whitespace, quotes, command expansions already present in input, and `$` variable substitutions.
- `nextword()` combines literal buffer content with substituted word lists, preserving mk list expansion semantics.
- `wtos()` and `bufcpyw()` convert word lists back to rc-quoted strings.

Important dependencies: `mk.h`, `expandquote`, `varsub`, `bufcpyq`.

Notable risks:
- Variable expansion can restart token parsing when empty at word start.
- Concatenating literal prefixes/suffixes with multi-word variable expansion is behaviorally important.
