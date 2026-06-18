# File Research: sources/os/plan9/9front/sys/src/cmd/vac/glob.c

Purpose: Converts Vac include/exclude glob syntax to regular expressions and evaluates path filters.

Key behavior:
- `glob2regexp` converts `*`, `...`, `?`, character classes, and negated character classes into anchored Plan 9 regexp syntax.
- Treats `*` and `?` specially at the beginning of path elements so dot files are not matched by default.
- `loadexcludefile` reads `include PATTERN` and `exclude PATTERN` lines, ignoring blank lines and comments.
- `excludepattern` appends a command-line exclude rule.
- `includefile` returns the first matching pattern’s include flag, defaulting to include.

Dependencies:
- Uses `Biobuf`, `regexp`, `isspace`, Venti allocation helpers, and `sysfatal` for invalid pattern files.

Notable details:
- Pattern order matters: the first regexp match decides inclusion.
