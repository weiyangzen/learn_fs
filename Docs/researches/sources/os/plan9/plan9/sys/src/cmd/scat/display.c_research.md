# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/display.c

Displays generated sky images by piping them to `/bin/page`.

Key functions:
- `displaypic` writes a raw `k8` image header and pixel bytes from a `Picture` to a child `page -w` process.
- `displayimage` writes a Plan 9 `Image` with `writeimage` to a child `page -w` process.

Behavior notes:
- Both functions fork with `rfork(RFPROC|RFFDG|RFNOTEG|RFNOWAIT)`.
- `displaypic` frees page-aligned chunks with `segfree` when possible, then frees picture storage.
- Pipe/fork/exec/write failures are reported but generally do not abort the main process.
