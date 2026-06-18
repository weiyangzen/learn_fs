# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/rules.c

Parser, printer, variable expander, and incremental updater for plumber rules.

Key responsibilities:
- Maintains a nested input stack for rule files and string updates.
- Parses variables, includes, rules, rulesets, and port declarations.
- Validates object/verb combinations and compiles regex rules.
- Expands `$0`-style regex matches, message fields, variables, `$file`, and `$dir`.
- Serializes rules back to text for reading `/mnt/plumb/rules`.
- Incrementally accepts rule text written to the mounted `rules` file.

Important behavior:
- Include stack depth is capped at 10.
- Include paths that are not absolute or relative are searched under `/sys/lib/plumb`.
- Rulesets must have patterns and an action, except bare `plumb to` declarations, which declare ports.
- Only one `start` or `client` action is allowed per ruleset.
- `writerules()` parses complete rules as blank-line-delimited chunks during writes and finalizes on close.

Dependencies:
- Uses regexp compilation, plumb attribute packing, and globals from `plumber.h`.

Notable risks:
- `expand()` uses a fixed 4096-byte static buffer.
- `dollar()` has a likely typo checking `n == 4` but comparing `"wdir"` with length 3.
- Incremental parsing uses heuristics; malformed partial writes may report at write or close time depending on blank lines.
