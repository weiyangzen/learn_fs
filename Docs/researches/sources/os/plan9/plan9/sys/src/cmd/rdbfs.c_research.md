# File Research: sources/os/plan9/plan9/sys/src/cmd/rdbfs.c

Read status: complete, 437 lines.

`rdbfs` is a remote debugging filesystem. It mounts a synthetic `/proc/<proc>`-like tree backed by a serial line protocol, exposing files such as `ctl`, `kregs`, `mem`, `text`, and `status`.

The file implements a small memory-read cache keyed by address/count, with pages stored in hash buckets and recycled through a free list. Serial communication is handled in `eiaread`, which sends `r...` and `w...` commands and parses `R...` and `W...` responses.

The 9P service callbacks are `fsopen`, `fsread`, and `fswrite`. Reads and writes for `mem` and `kregs` are sent to the serial worker through `rchan`; `text` reads are served from the configured kernel text image; `ctl` accepts `kill`, `exit`, `refresh`, and `hashstats`.

`threadmain` parses options, configures the serial port, starts the serial worker, builds the synthetic tree, and mounts it before `/proc`.

Filesystem relevance: central. It is a user-level 9P filesystem that presents remote debugger state through Plan 9 file interfaces.
