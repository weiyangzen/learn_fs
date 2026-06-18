## sources/user-network-fs/gcsfuse/cfg/constants.go

Purpose: Centralizes configuration constants for logging, metadata cache sentinels, TTL limits, stat cache sizing, config keys, and cache alignment.

Important APIs/types/functions: severity constants `TRACE` through `OFF`; log format constants; metadata prefetch modes `disabled`, `sync`, `async`; `maxSequentialReadSizeMB`; `maxSupportedTTLInSeconds`/`maxSupportedTTL`; sentinels `TtlInSecsUnsetSentinel` and `StatCacheMaxSizeMBUnsetSentinel`; stat cache entry size assumptions; Viper key constants; `maxSupportedStatCacheMaxSizeMB`; `CacheUtilMinimumAlignSizeForWriting`; `ConfigFileFlagName`.

Control flow: no functions; constants are evaluated at compile time.

State and persistence: none.

Dependencies and integration points: imports `math`, `time`, and internal `util` for maximum MiB value. Used by config parsing, validation, rationalization, cache behavior, and tests.

Risks: sentinel values must remain impossible or highly improbable for user-set values. Stat cache average sizes affect capacity-to-MB rationalization and memory expectations. Changing config key strings breaks Viper binding/rationalization.

Test signals: indirectly covered by config utility, validation, rationalization, and decode tests.
