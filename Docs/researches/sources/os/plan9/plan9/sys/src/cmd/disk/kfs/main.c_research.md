# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/main.c

This file is the KFS program entry point and process orchestration layer.

Startup flow:
- Parses options for block size, no-check, filesystem file, multi-wren count, service name, command mode, ream, stdin/stdout service mode, buffer count, and chat.
- Insulates namespace/environment with `rfork`, disables swapping through `/proc`, checks access to `wrenfile`.
- Initializes formatting, allocator locks, service name, service channel, console channel, lock tables, uid/gid tables, and `mainlock`.
- Calls `fsinit`, `iobufinit`, `rootream`, and `superream` as needed.
- Runs console bootstrap commands via `consserve`.
- Marks filesystem not-ok while running via `superok`; optionally runs `check fq` after unclean shutdown.
- Starts `forkserve` and `syncproc`.

Runtime services:
- `syncproc` creates `/srv/<service>.cmd`, periodically flushes dirty blocks, reads operator commands, and updates load filters.
- `netserve` announces a network address and forks a server per accepted connection.
- `chaninit` registers the main `/srv/kfs` service fd.
- `consinit` creates the internal console channel and registers stats filters.
- `fsinit` initializes devices, decides ream/check behavior, computes block-size-dependent constants.
- `iobufinit` sizes and initializes the buffer cache.

Notable details:
- `memsize` estimates memory from `/dev/swap` and uses about one tenth for buffer cache if `-B` is not supplied.
- `fsok` is cleared on startup and restored by `halt`; this lets the next startup detect unclean shutdown.
