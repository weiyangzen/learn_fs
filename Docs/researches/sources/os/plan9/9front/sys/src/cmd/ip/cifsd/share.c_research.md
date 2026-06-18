# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/share.c

Implements CIFS share mapping for `cifsd`. `mapshare` derives a share name from a requested SMB path, rejects unsafe names, special-cases `local` and `IPC$`, and lazily creates a `Share` record with filesystem/service metadata.

`run9fs` forks `/bin/9fs <share>` to populate `/n/<share>` for normal disk-tree shares, redirecting child output to `/sys/log/<progname>`. The share list is process-global and reused by name.

Notable dependencies: `unixidmap`, `logit`, `strtr`, Plan 9 namespace convention `/n/<name>`.
