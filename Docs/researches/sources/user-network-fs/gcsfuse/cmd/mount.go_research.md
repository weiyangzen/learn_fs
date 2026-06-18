# sources/user-network-fs/gcsfuse/cmd/mount.go

## Purpose
`mount.go` converts a mount-ready `cfg.Config` plus a storage handle into a live FUSE mounted filesystem. It builds gcsx bucket configuration, filesystem server configuration, and jacobsa/fuse mount configuration.

## Important APIs And Functions
The main function is `mountWithStorageHandle(ctx, bucketName, mountPoint, newConfig, storageHandle, metricHandle, traceHandle, viperConfig) (*fuse.MountedFileSystem, error)`. `getFuseMountConfig(fsName string, newConfig *cfg.Config) *fuse.MountConfig` creates low-level FUSE mount options. The function uses `gcsx.BucketConfig`, `fs.ServerConfig`, and `fuse.MountConfig` as integration data structures.

## Control Flow And State
`mountWithStorageHandle` first verifies `TempDir` by creating an anonymous temp file, then determines current UID/GID and warns if running as root without an explicit UID. Config-provided UID/GID override process ownership. It builds `gcsx.BucketConfig` from billing, rate limits, stat cache size and TTL, retry chunk deadlines, dummy I/O, type-cache deprecation, and implicit-dir settings. It then builds `fs.ServerConfig` with cache clock, bucket manager, permissions, mount behavior, metadata TTLs, read size, new config, Viper config, metrics, and tracing. If dentry cache is enabled it attaches a FUSE notifier. It creates the server and calls `fuse.Mount`.

## Dependencies And Integration
The file depends on cfg, internal mount option parsing, storage, fs, gcsx, logger, perms, metrics/tracing, jacobsa/fuse, fsutil, and timeutil. `legacy_main.go` calls this after storage and monitoring setup. The resulting mount config controls FUSE options, parallel directory operations, writeback caching disabled for streaming writes, ReaddirPlus, async reads for kernel reader mode, wire logging, and FUSE error/debug loggers based on log severity rank.

## Risks And Test Signals
Risks include narrowing signed config values to unsigned cache sizes after rationalization, temp-dir validation panic risk if `AnonymousFile` returns nil before close, permission surprises when running as root, and side effects from creating/truncating wire logs. FUSE logger mapping intentionally logs errors for severities ERROR through TRACE but disables at OFF. `cmd/mount_test.go` covers mount option parsing for comma and list formats, FUSE logger initialization thresholds, and ReaddirPlus propagation; real FUSE mount behavior needs integration coverage.
