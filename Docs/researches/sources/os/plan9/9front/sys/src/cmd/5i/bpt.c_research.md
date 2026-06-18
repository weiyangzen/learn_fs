# File Research: sources/os/plan9/9front/sys/src/cmd/5i/bpt.c

This file implements breakpoints for `5i`.

Key routines:
- `dobplist()` prints all breakpoints with address, count/done state, type-specific prefix, and symbolized location.
- `breakpoint(addr, cp)` parses breakpoint subtype:
  - default instruction breakpoint,
  - `r` read,
  - `a` access,
  - `w` write,
  - `e` equal-value watchpoint.
  It evaluates the address, records `cmdcount`, initializes `done`, and prepends to `bplist`.
- `delbpt(addr)` removes a breakpoint at an evaluated address.
- `brkchk(addr, type)` checks breakpoints against an access/instruction event, handles equal-value watchpoints through `getmem_4()`, decrements count-based breakpoints, and stops execution through `count=1` and `atbpt=1`.

Dependencies and interactions:
- Memory accessors in `mem.c` call `brkchk()` for read/write watchpoints.
- Execution loop calls it for instruction breakpoints elsewhere in `5i`.
- Command parser in `cmd.c` drives breakpoint creation/deletion.

Research relevance:
- Interactive debugging control for `5i`.

Risk notes:
- `delbpt()` increments `membpt` instead of decrementing for non-instruction breakpoints; this keeps checks enabled but looks like a counter bug.
- Equal breakpoints use `count` as comparison value, unlike count-based breakpoints.
