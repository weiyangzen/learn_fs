# File Research: sources/windows/winfsp/src/dll/fuse/fuse_main.c

This file implements the FUSE 2-style main entry flow.

Key responsibilities:
- Defines command-line options for help, debug/foreground, foreground, and single-thread mode.
- `fsp_fuse_parse_cmdline` extracts the mountpoint and returns multithread/foreground decisions while preserving or forwarding relevant options.
- `fsp_fuse_main_real` performs the standard lifecycle:
  1. Parse command line.
  2. Mount/create a `fuse_chan`.
  3. Create a `struct fuse`.
  4. Daemonize if needed.
  5. Install signal handlers.
  6. Run `fsp_fuse_loop` or `fsp_fuse_loop_mt`.
  7. Tear down signal handlers, fuse object, channel, mountpoint, and args.

Filesystem relevance:
- This is the compatibility entry point for FUSE applications that expect `fuse_main`-like behavior on Windows.
- It is orchestration glue; real filesystem behavior is delegated to `fuse_loop.c`, `fuse_intf.c`, and the application callback table.
