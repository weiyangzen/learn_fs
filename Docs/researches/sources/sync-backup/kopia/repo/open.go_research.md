# sources/sync-backup/kopia/repo/open.go

Purpose: contains repository open logic for local/direct blob access and API-server access. It builds the storage, cache, format, content, object, manifest, metrics, throttling, logging, retention, and close-management layers.

Important APIs/types/functions: `Options` controls tracing, content logs, time source, repository log disabling, upgrade behavior, callbacks, fatal handling, and test-only feature ignoring. Public `Open` dispatches between API server and direct configurations. Internal helpers include `getContentCacheOrNil`, `openAPIServer`, `openDirect`, `openWithConfig`, `deriveHMACSecret`, `handleMissingRequiredFeatures`, `wrapLockingStorage`, `addThrottler`, `upgradeLockMonitor`, and `throttlingLimitsFromConnectionInfo`.

Control flow: `Open` normalizes the config path, loads local config, rejects writable permissive cache loading, and dispatches to API-server or direct open. Direct open creates blob storage, wraps read-only storage if needed, applies client defaults, then `openWithConfig` creates format manager, checks required features, derives cache HMAC secret, applies throttling, retention locks, upgrade-lock waiting/monitoring, diagnostics logging, content manager, write manager, object manager, manifest manager, and ref-counted closer. API open derives a password-protected persistent content cache, creates immutable server parameters, and opens the gRPC repository.

State and persistence behavior: reads config and format/blobcfg blobs; may update config throttling when throttler settings change. It derives cache integrity/encryption material from repository secrets and password. Retention-enabled repositories wrap `PutBlob` options for protected prefixes. Upgrade monitoring checks format-manager loaded time on storage operations and may fatal-error on unsupported features.

Dependencies/integration: integrates with `blob.NewStorage`, `readonly`, `beforeop`, `storagemetrics`, `throttling`, `format.Manager`, `content.NewSharedManager`, `object.NewObjectManager`, `manifest.NewManager`, `repodiag`, feature gating, and cache protection.

Risks: open order is security-sensitive: feature and upgrade checks must happen before normal repository IO. Cache key derivation must match server repository settings or cache reads fail. `upgradeLockMonitor` invokes `OnFatalError`, which defaults to `os.Exit(1)`, so tests override or set test flags. Retention wrapping must only affect repository-managed blob prefixes.

Test signals: repository tests cover password changes, retention blob behavior, write sessions, derived keys, metrics, and API server callback behavior. Feature/upgrade paths are likely covered elsewhere in the repo.
