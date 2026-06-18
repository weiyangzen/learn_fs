# File Research: sources/os/plan9/9front/sys/src/9/port/mkbootrules

`rc`/`awk` generator for mkfile rules that embed `bootdir` files into kernel root images.

Key responsibilities:
- Parses configuration sections, collecting indented entries from `bootdir`.
- Derives filesystem-visible names and C-safe symbol names.
- Emits rules for `<CONF>.root.s` using `mkrootall`.
- Emits rules for `<CONF>.rootc.c` using `mkrootc`.
- Passes all collected `name cname file` triples to the root generators.

Important behavior:
- If a bootdir entry has a second field, that is the embedded file name; otherwise basename is used.
- C symbol names replace non-alphanumeric/underscore characters with `_`.

Dependencies:
- Uses Plan 9 `rc`, `awk`, and mkfile `$target` conventions.
