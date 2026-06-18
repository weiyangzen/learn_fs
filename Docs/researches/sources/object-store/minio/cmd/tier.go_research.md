# sources/object-store/minio/cmd/tier.go

Purpose: central configuration and metrics manager for MinIO remote transition tiers. It validates remote tier definitions, caches warm backend drivers, serializes tier config, persists it to MinIO metadata storage, reloads it across distributed nodes, and exposes tier metrics.

Important APIs and types: `TierConfigMgr` holds a mutex, `drivercache`, `Tiers` map, and `lastRefreshedAt`. Methods include `Add`, `Remove`, `Verify`, `Edit`, `Bytes`, `configReader`, `getDriver`, `Reload`, `Save`, `Init`, `ListTiers`, `IsTierValid`, `TierType`, and `Empty`. `tierMetrics` records Prometheus TTLB histograms plus success/failure counters, with `Observe`, `logSuccess`, `logFailure`, and `Report`. Config constants define `tier-config.bin`, format/version headers, and `tierConfigPath`.

Control flow: `Add` validates uppercase unique names, creates a warm backend, optionally checks `InUse`, and inserts config/driver. `Remove` resolves the driver, optionally rejects non-empty/in-use backends, then deletes config/cache entries. `Edit` updates credentials by tier type, rebuilds the warm backend, and replaces the cache. `Bytes` prefixes msgp data with two little-endian uint16 headers for format and version. `configReader` wraps bytes in a hash reader and optionally encrypts with KMS before `Save` writes to `minioMetaBucket/tier-config.bin`. `Reload` calls `loadTierConfig`, clears cache and current tiers, copies loaded tiers, and updates refresh time. `Init` reloads once and starts periodic jittered refresh in distributed erasure mode.

State and persistence: authoritative tier config is persisted as a msgpack blob in the metadata bucket, optionally encrypted when KMS is enabled. In-memory state includes the tier map, cached `WarmBackend` drivers, metrics counters, and last refresh timestamp. `drivercache` is intentionally not serialized.

Dependencies and integration points: integrates with `madmin.TierConfig`, warm backend constructors/checks, `ObjectLayer` config storage, KMS/S3 encryption helpers, hash readers, Prometheus metrics, admin handlers, lifecycle transition code, and distributed notification/refresh behavior.

Risks: `Save` calls `globalTierConfigMgr.configReader(ctx)` instead of the receiver's `configReader`, so alternate manager instances must be treated carefully. Concurrent admin updates rely on locking inside the manager but persistence-level lost updates remain a consideration. Credential edit validation differs by tier type; missing GCS/MinIO credentials fail explicitly, while S3/Azure allow partial updates. Backward compatibility depends on preserving header format/version handling.

Test signals: `tier_test.go` covers metrics counter reporting. Generated msgp tests cover serialization plumbing. Additional coverage should focus on add/edit/remove validation, KMS and non-KMS `configReader`, load version errors, reload-not-found behavior, and concurrent edits.
