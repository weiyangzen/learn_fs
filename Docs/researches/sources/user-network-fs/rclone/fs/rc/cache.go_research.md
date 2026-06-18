# Research: sources/user-network-fs/rclone/fs/rc/cache.go

## sources/user-network-fs/rclone/fs/rc/cache.go

Purpose: provides rc helpers for resolving filesystem parameters and exposes fs-cache rc endpoints. APIs include `GetFsNamed`, `GetFsNamedFileOK`, `GetFs`, `GetFsAndRemoteNamed`, `GetFsAndRemote`, plus registered `fscache/clear` and `fscache/entries`.

Control flow parses a named parameter as either a string fs path or a structured config map. Structured configs use `type` or `_name`, optional `_root`, and remaining config values to build an fspath. `GetFsNamedFileOK` handles `fs.ErrorIsFile` by adding a single-file filter to a new context. State/persistence lives in the global `fs/cache` package; this file only clears or counts it. Dependencies include `cache.Get`, `configmap.Simple`, `filter`, and `fspath.Split`. Integration points are nearly all rc operation handlers. Risks include structured config string escaping, rejecting single-file limiting when filters are already active, global cache invalidation through `fscache/clear`, and parameter type ambiguity. Tests cover string, struct, single-file, and cache endpoints.
