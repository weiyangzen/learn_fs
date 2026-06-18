# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/main.c

Purpose: 9P server front-end for serving ISO images.

Key behavior: parses options for stdio/service mode, default image, cache clusters, chatty mode, and format-disabling flags. Publishes `/srv/<name>` unless in stdio mode, then handles 9P messages in `io`. Request handlers implement version, attach, walk with partial-walk recovery, open, read, clunk, stat, and read-only rejection for create/write/remove/wstat.

Integration notes: delegates filesystem-specific operations through `Xfsub`. Uses a jump-buffer error stack for per-request errors and `xfile.c` for fid/device lifecycle.
