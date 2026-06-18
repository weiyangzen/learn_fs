## sources/sync-backup/kopia/internal/blobtesting/storage.go

Purpose: declares a test-only retention-capable storage interface.

Important APIs/types/functions: `RetentionStorage`.

Control flow, state, and persistence: no implementation; interface embeds `blob.Storage` and adds `TouchBlob` plus `GetRetention`.

Dependencies and integration points: implemented by `objectLockingMap`; used by tests needing retention inspection and mutation simulation.

Risks and test signals: interface shape must track provider capabilities used in object-lock tests. No direct tests needed beyond implementer checks.
