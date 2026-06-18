# sources/user-network-fs/rclone/vfs/vfscommon/options.go

## Purpose
Defines the global VFS option schema and the runtime `Options` struct used to configure rclone's VFS and mount behavior.

## APIs, Flow, And State
`OptionsInfo` lists all registered VFS options: modtime/checksum/seek behavior, directory cache and polling, read-only and symlink handling, cache mode and cache limits, read chunking, permissions/uid/gid, case handling, write/read waits, writeback delay, read-ahead, used-size algorithm, fingerprint mode, disk space reporting, handle caching, and metadata extension. `init` registers these global options as `vfs`. `Options` mirrors the config keys. `Init` applies global `--links`, masks permissions by umask, and forces directory and symlink mode bits.

## Dependencies And Integration
Depends on `fs.Options`, `fs.Duration`, `fs.SizeSuffix`, platform-specific `getUmask/getUID/getGID`, `CacheMode`, and `FileMode`. Every VFS, cache, writeback, mount, and functional test path consumes this struct.

## Risks And Test Signals
Defaults are behavioral contract: changing cache/writeback/handle-caching defaults affects IO timing and persistence. Permission normalization is platform-sensitive. Direct tests are light, but broad signal comes from VFS and vfstest suites using `vfscommon.Opt` and calling `Init`.
