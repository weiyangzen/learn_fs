# File Research: sources/os/plan9/9front/sys/src/cmd/pic/movegen.c

`movegen.c` implements `MOVE` object generation. It interprets move attributes such as `left`, `right`, `up`, `down`, `same`, `to`, `by`, `from`, and `at`, updates `curx/cury`, records text attributes attached to moves, and remembers the previous move delta for `same`.

If no explicit directional or positional attribute is supplied, it moves by the default `movewid`/`moveht` in the current `hvmode`. It records extrema before and after the move, then creates a zero-count `MOVE` node.
