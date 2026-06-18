# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/list.c

Read status: complete, 96 lines.

This file implements a small generic dynamic list abstraction used by `sam` for position lists and pointer lists. `growlist` allocates or extends capacity by `INCR`. `inslist` inserts a `Posn` or pointer with varargs. `dellist` removes an element. `listalloc` and `listfree` manage list lifetime.

Filesystem relevance: no direct filesystem logic, but used by editor state such as file lists, parse object lists, and ranges.
