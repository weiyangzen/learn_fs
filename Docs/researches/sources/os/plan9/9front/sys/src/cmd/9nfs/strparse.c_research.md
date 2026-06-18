# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/strparse.c

Small whitespace tokenizer for 9nfs configuration lines.

Key responsibilities:
- Splits a mutable string into argv-style fields separated by spaces or tabs.
- Stops parsing at NUL or the configurable comment character `strcomment`.
- NUL-terminates fields in place and returns the argument count.

Important behavior:
- Leaves `arv[arc]` as nil.
- Reserves one argv slot for the terminating nil by stopping at `arsize-1`.

Dependencies:
- Standalone Plan 9 libc file.

Notable risks:
- Does not support quoting or escaping; config files using spaces inside fields cannot be represented.
