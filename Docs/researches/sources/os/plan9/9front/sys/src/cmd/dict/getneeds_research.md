# File Research: sources/os/plan9/9front/sys/src/cmd/dict/getneeds

Debug-log postprocessor for missing OED/PGW-style markup needs.

Key elements:
- Iterates categories `spec`, `tag`, `aux`, and `status`.
- Greps matching diagnostics from an input file.
- Sorts and deduplicates by diagnostic fields.
- Emits `needspec`, `needtag`, `needaux`, and `needstatus` files.

Dependencies:
- Uses Plan 9 `rc`, `grep`, `sort`, `awk`, and temporary `junk*` files.

Research notes:
- Intended for maintaining markup translation tables by extracting unknown tokens from debug output.
