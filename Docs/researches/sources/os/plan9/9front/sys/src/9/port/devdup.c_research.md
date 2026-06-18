# File Research: sources/os/plan9/9front/sys/src/9/port/devdup.c

Purpose: duplicate-file-descriptor device `#d`, presenting the current process file group as files.

Exposed interface: each fd appears as `<fd>` and `<fd>ctl`. Qid encoding is `(2*fd + isctl) + 1`.

Core implementation: `dupgen` iterates `up->fgrp->fd`, derives permissions from the target Chan mode for fd files, and exposes ctl files as readable. `dupopen` rejects `ORCLOSE`; opening an fd file returns `fdtochan` and closes the original `#d` Chan, while opening a ctl file opens the synthetic Chan. `dupread` on ctl files formats fd metadata using `procfdprint`.

Dependencies: process file group, `fdtochan`, and standard devwalk/devstat helpers.

Research notes: behavior is intentionally process-local and minimal. Review focus is qid/fd decoding, permissions mirroring, and ensuring ctl opens do not accidentally confer operations on the underlying fd.
