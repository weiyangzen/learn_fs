# File Research: sources/os/plan9/9front/sys/src/cmd/grap/print.c

Final pic output arranger for `grap`. `print` closes the temporary generated-body file, computes coordinate extents with margins/log transforms, emits `xy_`, `x_`, and `y_` mapping macros for each coordinate object, writes frame/autoticks, then copies temporary drawing content.

`graph` flushes prior graph blocks and starts named graph blocks, enforcing capitalized names. `setup`, `do_first`, `reset`, and `opentemp` initialize each `.G1`/graph, load library definitions once, preserve definitions and variables across graph resets, and reset per-graph rendering state.
