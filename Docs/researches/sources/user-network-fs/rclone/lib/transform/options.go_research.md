# sources/user-network-fs/rclone/lib/transform/options.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/options.go -->
## sources/user-network-fs/rclone/lib/transform/options.go

Purpose: parses and caches `--name-transform` options into internal transform descriptors.

Important APIs and control flow: `Transforming(ctx)` checks `fs.ConfigInfo.NameTransform`. `SetOptions(ctx, s...)` overwrites that config slice and forces parsing. `getOptions(ctx)` returns cached parsed transforms when the configured slice equals `cachedNameTransform`; otherwise it parses each string and updates the cache. `parse` strips optional `file,`, `dir,`, or `all,` tags, then parses a key or `key=value`. `requiresValue` marks transforms that require a value. `Algo` and `transformChoices` define all supported transform names.

State, dependencies, and integration: package cache state includes `cachedNameTransform`, `cachedOpt`, and `cacheLock`. The initial cache equality check is outside the lock, while updates are locked. It depends on `context`, `errors`, `slices`, `strings`, `sync`, and rclone `fs`. It integrates with `transform.Path`.

Risks and test signals: `strings.Split(s, "=")` rejects values containing `=`, which may limit regex/command/value transforms. Cache reads are not fully locked, so concurrent config changes could race unless higher-level config access is serialized. `ConvIndex` requires a value but is not implemented in `transform.go`. Tests cover high-level option parsing and tag behavior through `Path`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/options.go -->
