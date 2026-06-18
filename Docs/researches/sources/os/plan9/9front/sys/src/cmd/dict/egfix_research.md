# File Research: sources/os/plan9/9front/sys/src/cmd/dict/egfix

`rc`/`sed` cleanup pipeline for English-German index material.

Key elements:
- Removes trailing whitespace.
- Drops lines without tabs.
- Splits comma-separated alternatives into additional index lines.
- Expands parenthesized variants by emitting both forms.
- Normalizes repeated spaces and tab spacing.

Dependencies:
- Uses Plan 9 `rc` and `sed`.
- Takes an input filename as `$1`.

Research notes:
- This is a preprocessing helper for raw dictionary index generation, not runtime `dict` code.
