# File Research: sources/os/plan9/plan9/sys/src/9/port/mkfilelist

Purpose: rc helper that lists `.c` files in a directory excluding files already present in the current directory.

Key logic:
- With one argument, builds a regex from local `*.c`.
- Lists `*.c` in the target directory, filters out matching local files, removes `.c` suffixes, and joins names with `|`.
- If local `*.c` glob is literal, lists all target `.c` files.

Dependencies and integration:
- Uses `rc`, `ls`, `grep`, and `sed`.

Risks and notes:
- Intended for build-rule generation; output is a regex-style alternation string.
