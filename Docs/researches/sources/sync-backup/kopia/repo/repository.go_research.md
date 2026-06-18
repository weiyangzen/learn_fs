# sources/sync-backup/kopia/repo/repository.go

Purpose: defines the public repository interfaces and implements direct repository operations for objects, manifests, write sessions, flushing, key derivation, metrics, and lifecycle.

Important APIs/types/functions: interfaces `Repository`, `RepositoryWriter`, `RemoteRetentionPolicy`, `RemoteNotifications`, `DirectRepository`, and `DirectRepositoryWriter` define the repo surface. `directRepository` holds blob/content/object/manifest managers and immutable parameters. Key functions include `NewDirectWriter`, `Flush`, `WriteSession`, `DirectWriteSession`, `replaceManifestsHelper`, and `handleWriteSessionResult`.

Control flow: read APIs delegate to object/content/manifest managers. `NewDirectWriter` creates an isolated content write manager, manifest manager, and object manager with a unique writer ID, then increments the shared closer reference. `Flush` runs before callbacks, flushes manifests then contents, and runs after callbacks. `WriteSession` and `DirectWriteSession` create writers, run callbacks, flush on success or configured failure, and close writers in a defer.

State and persistence behavior: write sessions isolate unflushed content visibility until `Flush`. Manifests are persisted via `PutManifest`/`ReplaceManifests`; content/index blobs persist through content manager flushes. `DeriveKey` uses either master key for password-change-capable formats or legacy format encryption key for old/upgraded v1 repositories. `UpdateDescription` mutates client options in memory.

Dependencies/integration: integrates `object.Manager`, `content.WriteManager/SharedManager`, `manifest.Manager`, `format.Manager`, blob storage, throttling, metrics, diagnostics, OpenTelemetry tracing, and snapshot policy callbacks.

Risks: write-session flush semantics are critical: errors should not flush unless `FlushOnFailure` is true. `replaceManifestsHelper` sleeps to avoid Windows timestamp flakiness, which can slow tight loops. `Close` handling relies on ref-count balance. `DeriveKey` must preserve legacy behavior for upgraded repositories.

Test signals: repository tests cover writer isolation/visibility, flush on success/failure, callbacks, object reads, metrics, retention, and key derivation across formats.
