# File Research: sources/os/plan9/9front/sys/src/cmd/dict/rev.awk

Small AWK field reverser for two-field index lines.

Key elements:
- For `NF == 2`, prints `$2<TAB>$1`.
- For malformed records, prints `ERROR` plus the record.

Dependencies:
- Standalone AWK script.

Research notes:
- Useful for converting `offset<TAB>key` style data into `key<TAB>offset`.
