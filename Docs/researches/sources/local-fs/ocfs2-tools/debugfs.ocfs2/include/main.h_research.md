# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/main.h

## Role

`main.h` is the central include and shared state definition for `debugfs.ocfs2`.

## Shared State

`struct dbgfs_gbls` stores program name, write/image/interactive flags, current device, open `ocfs2_filesys`, current/root directories, active command name, reusable block buffer, filesystem size limits, root/system/heartbeat/slotmap block numbers, and per-slot journal inode block numbers.

`struct dbgfs_opts` stores parsed command-line options before they are applied to global state.

## Includes And Macros

It enables GNU and large-file APIs, includes libc, GLib, readline, Linux type headers, libocfs2 headers, and all debugfs module headers. It defines fatal/warning macros, `min`/`max`, and a swap helper.

## Architectural Impact

Because most modules include this file, it centralizes dependencies and makes `gbls` the dominant cross-module coordination mechanism.
