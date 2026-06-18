# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/egfix2

This rc script builds an inverted, normalized index from comma/tab-separated data.

Key behaviors:
- Uses AWK with field separators tab or comma-space.
- For every field after the first, prints `term<TAB>offset`.
- Lowercases A-Z with `tr`.
- Sorts uniquely with folded-key and numeric-offset ordering.

Notable implementation details:
- Compact helper for converting multi-term raw records into `dict` index records.
