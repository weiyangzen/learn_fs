# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/translate.c

`translate()` runs a translation command from `dp->repl1`, reads stdout as a whitespace-separated destination list, recognizes `_nosummary_` control lines, converts output to child destinations via `s_to_dest()`, then reads stderr and waits.

A nonzero process status stores stderr in `dp->repl2` and returns no translated destinations. Process-start failure becomes `d_resource`.
