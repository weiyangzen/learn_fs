# File Research: sources/os/plan9/9front/sys/src/9/port/mkfilelist

`rc` helper that lists C source basenames in a directory while excluding already-present local `*.c` files.

Key behavior:
- Takes one directory argument.
- Builds a regular expression from `*.c` in the current directory.
- Lists `*.c` in the target directory, optionally filtering out names present locally.
- Strips `.c` suffixes and joins names with `|`.

Role:
- Supports mkfile pattern/list generation for shared source directories.
