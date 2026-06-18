## sources/user-network-fs/gcsfuse/internal/mount/flag.go

### Purpose
`flag.go` defines legacy mount flag defaults and a parser for comma-separated mount option strings.

### Important APIs, Types, And Functions
`ClientProtocol` has deprecated constants `HTTP1`, `HTTP2`, and `GRPC`, plus `IsValid`. Defaults include `DefaultStatOrTypeCacheTTL`, `DefaultStatCacheCapacity`, and `DefaultTypeCacheSizeMB`. `ParseOptions` populates a map from mount-style options.

### Control Flow
`IsValid` switches over the three known protocols. `ParseOptions` splits the input on commas, then splits each component at the first equals sign; options without `=` receive an empty value, and later duplicates overwrite earlier values.

### State, Persistence, And Dependencies
There is no persistent state. The caller-provided map is mutated. Dependencies are `strings` and `time`.

### Integration Points
This supports mount helpers and fstab-style option parsing. Deprecated protocol constants are retained for compatibility while newer code should use config package constants.

### Risks
There is intentionally no escaping or quoting, so commas cannot appear in names or values. Empty segments from leading/trailing/double commas produce empty-string keys. The parser does not trim whitespace.

### Test Signals
No tests in this shard. Useful tests would cover multiple equals signs, duplicate names, empty segments, whitespace, and protocol validation.
