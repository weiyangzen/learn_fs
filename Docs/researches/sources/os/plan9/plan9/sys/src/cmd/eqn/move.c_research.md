# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/move.c

Manual motion helper for `eqn`.

Key behavior:
- Applies horizontal forward/backward or vertical up/down troff motion around a box.
- Converts hundredths of em to current-size em units.
- Keeps the moved box register as the result.

Filesystem relevance:
- Typesetting layout only.
