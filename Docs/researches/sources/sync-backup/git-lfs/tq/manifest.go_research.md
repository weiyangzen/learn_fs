# sources/sync-backup/git-lfs/tq/manifest.go

Purpose: transfer adapter registry and transfer configuration manifest, lazily constructed from Git/LFS configuration.

Important APIs/types/functions: `Manifest`, `lazyManifest`, `concreteManifest`, `NewManifest`, `newConcreteManifest`, retry/concurrency getters, adapter-name getters, `RegisterNewAdapterFunc`, `NewAdapterOrDefault`, `NewAdapter`, `findStandaloneTransfer`, and `Env`.

Control flow: lazy manifest serializes first upgrade. Concrete construction reads retry, retry delay, concurrency, basic-only, standalone, TUS, and custom adapter config; configures SSH batch client when SSH transfer exists; registers basic, optional tus, SSH, and custom adapters; validates standalone custom agent. Adapter lookup falls back to basic when requested adapter is missing.

State and persistence: holds adapter factory maps, custom flags, config values, API client, filesystem, SSH transfer, and batch client; all in memory.

Dependencies and integration points: central dependency for `TransferQueue`, `Batch`, and all adapter registration functions. Integrates with `lfsapi.Client`, Git config, URL config, SSH transfer, and `lfshttp.DefaultConcurrentTransfers`.

Risks: adapter-name order is map iteration order unless basic-only. SSH without multiplexing forces concurrency to 1. Custom/standard name conflicts print warnings. Lazy upgrade must remain race-safe.

Test signals: `manifest_test.go` covers configurable/default retry behavior and concurrent upgrade; `transfer_test.go` covers adapter registration/fallback/basic-only behavior.
