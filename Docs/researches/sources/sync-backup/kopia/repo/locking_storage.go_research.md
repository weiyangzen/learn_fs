# sources/sync-backup/kopia/repo/locking_storage.go

Purpose: exposes the blob ID prefixes that maintenance retention extension should treat as repository-managed storage.

Important APIs/types/functions: `GetLockingStoragePrefixes`.

Control flow: returns a slice containing content pack prefixes, index blob prefix, epoch-manager prefixes, the maintenance schedule blob ID, format blob prefix, and log blob prefix.

State/persistence behavior: no state mutation; the returned prefix set defines which persisted blobs are considered for object-lock retention extension.

Dependencies/integration: depends on content, epoch, format, blob constants, and maintenance schedule/log blob naming.

Risks/test signals: missing a prefix would leave repository blobs with stale retention, while adding overly broad prefixes could extend unrelated objects. Coverage is indirect via retention extension tests.
