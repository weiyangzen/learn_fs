# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/egfix

This rc script normalizes raw English/German-style dictionary index data.

Key behaviors:
- Removes trailing whitespace.
- Drops lines without tabs.
- Splits comma-separated entries by emitting both the base term and a suffix-adjusted term.
- Expands parenthesized variants by emitting versions with and without parentheses.
- Collapses tab/space runs and trims trailing whitespace.

Notable implementation details:
- Implemented as a pipeline of three `sed` programs.
- Intended as a lightweight hand-cleanup helper before canonical sorting/indexing.
