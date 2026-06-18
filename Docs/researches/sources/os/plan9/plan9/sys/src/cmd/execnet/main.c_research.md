# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/main.c

Entry point for `execnet`.

Key behavior:
- Parses debug and `-n` name options.
- Defaults mount point to `/net`.
- Initializes the synthetic filesystem and posts/mounts it before the existing mount point with `threadpostmountsrv()`.
- Disables note group inheritance with `rfork(RFNOTEG)`.

Filesystem relevance:
- Mounts the `/net/exec` 9P service.
