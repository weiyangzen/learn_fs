# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mkconv

An rc script that converts older make/mk-style syntax into newer Plan 9 `mk` variable and recipe conventions.

Key behavior:
- Copies input through `tee` to a temporary file and transforms output through `sed`.
- Rewrites `$%`, `$@`, `$^`, `$?`, and `$((...))`-style variable references to mk internal variables like `${stem}`, `${target}`, `${prereq}`, and `${newprereq}`.
- Converts some leading recipe control syntax and `:&` rule syntax.
- Warns to stderr if recipes contain `cd` or `make`, since these need manual attention.
- Cleans up the temp file on exit/interruption.

Important dependencies: rc shell, `tee`, `sed`, `grep`, `$pid`.

Notable risks:
- This is heuristic text conversion, not a parser.
- Recipes with shell structure, `cd`, or recursive make need review after conversion.
