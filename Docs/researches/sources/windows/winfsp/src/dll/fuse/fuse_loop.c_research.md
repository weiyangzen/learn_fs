# File Research: sources/windows/winfsp/src/dll/fuse/fuse_loop.c

This file starts, runs, and stops the WinFsp dispatcher for a FUSE filesystem.

Key responsibilities:
- Starts a minimal WinFsp service thread via `FspServiceRun`.
- Initializes FUSE context and calls the filesystem `init` callback with a FUSE 2.8-like protocol view.
- Advertises WinFsp-specific capabilities such as readdir-plus, read-only, stat-ex, delete-access, and case-insensitive support.
- Probes `statfs`, root `getattr`, `readlink`, slash-dot symlink behavior, delete-access support, and xattr/EA support.
- Normalizes volume parameters including sector size, allocation unit, max component length, creation time, and serial number.
- Creates the `FSP_FILE_SYSTEM`, attaches `fsp_fuse_intf`, sets operation guards/debug logging, sets the mount point, and starts the dispatcher.
- Provides single-threaded and multithreaded loop entry points:
  - `fsp_fuse_loop` uses coarse operation guarding.
  - `fsp_fuse_loop_mt` uses fine operation guarding.
- Stops dispatcher and calls FUSE `destroy` during cleanup.
- Provides a Cygwin signal handler bridge.

Filesystem relevance:
- This file is where a user-mode FUSE instance becomes a live WinFsp filesystem.
- Capability probing here directly changes how `fuse_intf.c` behaves, especially for case sensitivity, symlink handling, EAs, and delete semantics.
