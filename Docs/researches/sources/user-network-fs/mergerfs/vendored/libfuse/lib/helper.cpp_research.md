# sources/user-network-fs/mergerfs/vendored/libfuse/lib/helper.cpp

## Purpose
`helper.cpp` provides libfuse-compatible high-level setup, mount, daemonize, command-line parsing, main loop entry, and teardown functions for mergerfs.

## Important APIs, Types, and Functions
Key exported functions are `fuse_parse_cmdline`, `fuse_daemonize`, `fuse_mount`, `fuse_unmount`, `fuse_setup`, `fuse_teardown`, and `fuse_main`. Internal helpers parse `-f`, mountpoint, fsname/subtype options, add default subtype, recover from disconnected mountpoints, call `fuse_kern_mount`, and centralize setup/teardown.

## Control Flow
`fuse_parse_cmdline` uses `fuse_opt_parse` to extract foreground and mountpoint while preserving relevant options. `fuse_mount_common` ensures fds 0-2 are open, calls platform `fuse_kern_mount`, and computes buffer size. `fuse_setup_common` parses options, mounts, creates `fuse_new`, daemonizes unless foreground, installs signal handlers, and returns the active `struct fuse`. `fuse_main` runs `fuse_loop_mt`, then tears down.

## State and Persistence
The helper owns the allocated mountpoint string, mount fd during setup, and process daemonization state. It does not persist configuration; it mutates process session/cwd/stdio during daemonization.

## Dependencies and Integration Points
It integrates `fuse_opt`, `fuse_lowlevel`, platform mount helpers, signal handlers, `fuse.cpp`, and the threaded loop. It is the main compatibility surface used by mergerfs startup.

## Risks
Daemonization changes cwd and stdio and uses a pipe to let the parent exit after initialization. Error paths must unmount and free mountpoint exactly once. Mountpoint realpath recovery may unmount disconnected FUSE mounts. Adding default subtype changes mount options based on argv[0].

## Test Signals
Test foreground/background startup, invalid/multiple mountpoints, disconnected mountpoint recovery, mount failure cleanup, fuse_new failure cleanup, signal setup failure, teardown after clearfd, and `fuse_main` return code mapping.
