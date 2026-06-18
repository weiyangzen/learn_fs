# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl.cc

## Purpose

This file implements OFS filesystem control operations. It handles legacy `fsctl()` commands such as locate/statfs/statls/statxa/statcc, routes v2 FSctl requests to cache, OSS, or plugin handlers, and forwards file-scoped fctl calls to an FSctl plugin.

## Important APIs, types, and functions

`XrdOfs::fsctl()` handles version-1 commands. Supported opcodes are `SFS_FSCTL_LOCATE`, `SFS_FSCTL_STATFS`, `SFS_FSCTL_STATLS`, `SFS_FSCTL_STATXA`, and `SFS_FSCTL_STATCC`. `XrdOfs::FSctl(const int, XrdSfsFSctl&, ...)` handles v2 plugin/cache/storage operations. `XrdOfs::FSctl(XrdOfsFile&, ...)` handles file-scoped control operations.

## Control flow

Locate splits path and opaque data, authorizes unless server selection is requested, optionally asks `Finder`, stats local OSS state, chooses server/read-write markers, and returns destination interface data. Statfs/statls authorize, optionally query remote finder space, then ask OSS for physical or logical space. Statxa locates if remote, asks OSS for extended stat data, appends authorization privilege letters, and returns data. Statcc returns cluster configuration status from `Finder` or `Balancer`, defaulting to `none|`.

V2 `SFS_FSCTL_PLUGXC` routes to `FSctl_PC` after optional read authorization. `SFS_FSCTL_PLUGFS` authorizes stat access, calls OSS `FSctl(XRDOSS_FSCTLFS, ...)`, and converts returned strings into `SFS_DATA`. Other v2 commands go to `FSctl_PI` if configured. File-scoped calls also require `FSctl_PI`.

## State and persistence behavior

No state is persisted here. The file reads runtime globals and member pointers: finder/balancer location services, network interface selection, OSS plugin, authorization plugin, cache/plugin handlers, and export/security environment data.

## Dependencies and integration points

It integrates with `XrdNetIF`, OFS security macros, `XrdCmsClient`, `XrdOss`, `XrdSfsFSctl`, `XrdSfsFAttr`, `XrdSecEntity`, `XrdOucEnv`, and `XrdOfsFSctl_PI`. It is an externally visible control surface for clients, cache plugins, OSS plugins, and FSctl plugins.

## Risks and test signals

Authorization and remote routing differ per opcode, so regressions can expose data or misroute requests. `STATXA` appends privilege data after the OSS buffer and assumes sufficient message buffer slack. `SFS_FSCTL_PLUGFS` mixes URL construction with opaque argument handling. Tests should cover each opcode, authorization denied paths, finder redirects/errors, IPv4/IPv6 destination selection, read-only and privilege letters, OSS negative/positive FSctl returns, absent plugins, and plugin forwarding.
