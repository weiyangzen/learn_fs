# File Research: sources/os/plan9/plan9/sys/src/9/port/devpipe.c

Implements `#|`, the Plan 9 pipe device. Each attach creates a new `Pipe` with two queue-backed endpoints exposed as `data` and `data1`.

The two data files are connected crosswise: reading `data` consumes queue 0 and writing `data1` writes queue 0; reading `data1` consumes queue 1 and writing `data` writes queue 1. Queue size defaults to `conf.pipeqsize`, with larger default on multiprocessor systems.

`Pipe` tracks qrefs for each endpoint and an overall reference count. Closing the last reference to either side hangs up the opposite queue and closes the local queue; once both qrefs are zero, both queues are reopened for reuse. Final close frees queues and the `Pipe`.

Directory/stat generation reports current queue lengths. `wstat` by `eve` can change endpoint permissions but not owner. Writes to closed pipes post a user note `"sys: write on closed pipe"` unless the channel is marked `CMSG` for mounted queue use.

The implementation provides both byte and block I/O paths (`pipewrite`/`pipebwrite`, `piperead`/`pipebread`) on top of kernel `Queue`s.
