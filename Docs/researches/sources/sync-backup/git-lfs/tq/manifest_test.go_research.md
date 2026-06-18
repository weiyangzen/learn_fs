# sources/sync-backup/git-lfs/tq/manifest_test.go

Purpose: tests manifest configuration defaults and lazy upgrade race safety.

Important APIs/types/functions: `TestManifestIsConfigurable`, `TestManifestClampsValidValues`, `TestLazyManifestConcurrentUpgrade`, and `TestManifestIgnoresNonInts`.

Control flow: builds clients with config maps, creates manifests, asserts retry values, and starts two goroutines that call `Upgrade` concurrently to ensure the same concrete instance is returned.

State and persistence: no durable state; in-memory clients/manifests.

Dependencies and integration points: uses `lfsapi`, `lfshttp`, `sync`, and `testify/assert`.

Risks: concurrency test only checks two goroutines and identity, not race detector output by itself.

Test signals: good coverage of retry config validation and lazy manifest locking.
