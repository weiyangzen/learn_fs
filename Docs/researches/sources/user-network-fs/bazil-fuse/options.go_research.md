# sources/user-network-fs/bazil-fuse/options.go

Purpose: `options.go` defines the public `MountOption` API and the internal `mountConfig` used to configure mount helper options and FUSE init feature flags.

Important APIs, types, and functions: `mountConfig` stores string mount options, `maxReadahead`, `initFlags`, `maxBackground`, and `congestionThreshold`. `escapeComma` escapes backslashes and commas for option strings. `getOptions` serializes the option map. Public options include `FSName`, `Subtype`, `DaemonTimeout`, `AllowOther`, `AllowDev`, `AllowSUID`, `DefaultPermissions`, `ReadOnly`, `MaxReadahead`, `AsyncRead`, `WritebackCache`, `CacheSymlinks`, `ExplicitInvalidateData`, `AllowNonEmptyMount`, `MaxBackground`, `CongestionThreshold`, `LockingFlock`, `LockingPOSIX`, and `HandleKillPriv`.

Control flow: `Mount` creates a config, then invokes each `MountOption` function. Options either add key/value strings for the platform mount helper or OR feature bits into `initFlags` for the FUSE init negotiation. `getOptions` escapes each key/value and joins with commas.

State and persistence behavior: Configuration is transient per mount. The map iteration order is not stable, but mount helpers treat options as a set.

Dependencies and integration points: Integrates with `fuse.Mount`, platform `mount` functions, and `initMount`. Feature flags are defined in `fuse_kernel.go`; platform-specific `DaemonTimeout` behavior lives in `options_freebsd.go` and `options_linux.go`.

Risks: Because options are stored in a map, duplicate keys overwrite previous values and serialized order is nondeterministic. Escaping is Linux-oriented; FreeBSD rejects commas before serialization. Some options are platform ignored or require system configuration, for example `AllowOther` needs `/etc/fuse.conf` on Linux.

Test signals: `options_test.go` validates FSName escaping for comma, whitespace, newline, and backslash; subtype; allow_other preconditions; default permissions; read-only; and mount acceptance for max background/congestion threshold.
