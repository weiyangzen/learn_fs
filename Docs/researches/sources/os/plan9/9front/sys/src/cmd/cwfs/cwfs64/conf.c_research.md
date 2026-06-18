# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/conf.c

Generic old-cw runtime defaults reused for a 64-bit build.

Important behavior:
- Same defaults as `cwfs/conf.c`: `main` at 2, `conf.nfile=40000`, dump enabled, message pool sizing.
- Protocol table exposes `serve9p2`.
