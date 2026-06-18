# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfssrv.c

Provides the `ext2srv` program entry point and server setup.

Key behavior:
- Parses flags for 9P debug, verbose logging, default device file, group/passwd maps, stdio serving, and read-only mode.
- Initializes the block cache with `iobuf_init()`.
- Serves either on stdio with `srv(&ext2srv)` or posts/mounts a named service with `postmountsrv()`.
- `xerrstr()` maps internal error numbers to strings from `errstr.h`.

Important implementation details:
- Defaults service name to `ext2`.
- If not verbose, stderr is redirected to `#c/cons`.
- `rdonly` controls device open mode and suppresses superblock dirtying in `ext2fs()`.

Risks and invariants:
- The commented notify handler indicates intended but disabled sync-on-note behavior.
- Uses global `errno` as the server error channel.
