# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/string.c

Implements mutable `Rune` string helpers used throughout host `sam`.

Key functions:
- `Strinit`, `Strinit0`, `Strclose`, and `Strzero` manage allocation and reset.
- `Strlen`, `Straddc`, `Strinsure`, `Strinsert`, `Strdelete`, `Strcmp`, and `Strispre` implement basic string operations.
- `Strtoc` converts a `String` to malloced UTF-8 bytes.
- `tmprstr`, `tmpcstr`, and `freetmpstr` build and release temporary `String` wrappers.

Behavior notes:
- `Strinsure` enforces `STRSIZE` and grows with slack.
- `Strzero` shrinks overly large buffers back toward `MAXSIZE`.
- `tmprstr` returns a static wrapper over caller-owned rune storage; callers must not free it with `freetmpstr`.
