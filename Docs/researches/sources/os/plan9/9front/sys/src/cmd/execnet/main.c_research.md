# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/main.c

This is the execnet command entry point.

Key responsibilities:
- Parses `-D` to enable chatty 9P diagnostics and `-n` to set the served protocol directory name.
- Accepts an optional mount point, defaulting to `/net`.
- Calls `rfork(RFNOTEG)`, installs quote formatting, initializes the filesystem, and posts/mounts the service with `threadpostmountsrv`.

Important implementation notes:
- Usage is `execnet [-n exec] [/net]`.
- `-n` changes the visible protocol directory name from `exec` to the supplied name.
- The service is mounted `MBEFORE`.
