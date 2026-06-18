# Research: sources/object-store/minio/cmd/bucket-quota.go

Purpose: implements bucket quota retrieval, cached bucket usage lookup, quota JSON parsing, and hard-quota enforcement before writes.

Important APIs and functions: `BucketQuotaSys.Get` loads quota config from `globalBucketMetadataSys.GetQuotaConfig`. `NewBucketQuotaSys` constructs the subsystem. `bucketStorageCache` caches `DataUsageInfo`. `BucketQuotaSys.Init` initializes a 10-second cache with last-good/no-wait options and a 2-second backend load timeout. `GetBucketUsageInfo` retrieves cached usage and logs fallback conditions. `parseBucketQuota` unmarshals `madmin.BucketQuota` and validates it, explicitly rejecting old `fifo` quota configs. `enforceQuotaHard` and package helper `enforceBucketQuotaHard` block writes that would exceed hard quota.

Control flow: quota enforcement ignores negative sizes, loads quota config, selects quota size from `Size` or legacy `Quota`, rejects if the incoming object size itself exceeds quota, then fetches cached bucket usage and rejects if current size plus incoming size reaches quota. Cache initialization is idempotent and uses the current object layer.

State and persistence behavior: quota configuration is persisted by bucket metadata elsewhere; this file reads it. Usage state is cached in-memory through `cachevalue` and populated from backend data usage. Enforcement uses cached usage, so it is approximate within cache freshness and backend load success.

Dependencies and integration points: integrates madmin quota types, bucket metadata system, data usage loader, cachevalue, object-layer initialization, MinIO logging, and write paths that call `enforceBucketQuotaHard`.

Risks: stale or missing usage data can allow temporary quota overshoot; when no reliable usage is available, enforcement may not block except for single object size exceeding quota. The comparison uses `>=`, so writes exactly reaching quota are rejected. `GetBucketUsageInfo` logs a formatting string inside `errors.New`, losing the bucket/error interpolation in one branch.

Test signals: no direct tests in this subset. Quota parsing, cache fallback, exact-boundary enforcement, and stale usage behavior need dedicated coverage elsewhere.
