# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tm.c

Splits numeric table fields into left and right parts for decimal alignment.

Key points:
- `maknew` searches a field for an explicit `\&` split marker, otherwise finds a decimal point outside `eqn` delimiters, otherwise finds the boundary after the final numeric run.
- If no numeric split point exists, returns `0` and leaves the field unsplit.
- Copies the right-hand part into reusable `exspace` storage and truncates the original string at the split point.
- `ineqn` tracks whether a candidate split position lies between equation delimiters `delim1` and `delim2`.

Dependencies and interactions:
- Uses `chspace`, `exstore`, `exlim`, `exspace`, `digit`, and global equation delimiters.
- Called when parsing numeric columns in normal and continuation table paths.

Research relevance:
- Provides `tbl`’s decimal/numeric alignment behavior.
