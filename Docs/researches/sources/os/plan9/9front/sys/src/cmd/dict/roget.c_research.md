# File Research: sources/os/plan9/9front/sys/src/cmd/dict/roget.c

Adapter for Project Gutenberg Roget’s Thesaurus.

Key elements:
- `rogetprintentry` extracts headwords in `h` mode by skipping numbering, punctuation, and bracketed material until `" -- "`.
- Full printing removes the leading number, formats first-line delimiter `" -- "`, handles continuation lines, and rewrites selected `&c` cross references as `/target/`.
- `rogetnextoff` finds the next line beginning with a digit and containing `" -- "`.
- `rogetprintkey` reports no pronunciation key.

Dependencies:
- Uses C `ctype` helpers and common output routines.

Research notes:
- Tailored to Gutenberg text layout rather than structured tags.
