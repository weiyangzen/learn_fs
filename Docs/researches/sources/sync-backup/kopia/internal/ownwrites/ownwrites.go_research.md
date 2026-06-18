# sources/sync-backup/kopia/internal/ownwrites/ownwrites.go

Purpose: wraps eventually consistent blob storage so recent local writes appear in listings and recent deletes disappear from listings.

Important APIs/types/functions: `CacheStorage`, `ListBlobs`, `PutBlob`, `DeleteBlob`, `NewWrapper`, `isCachedPrefix`, `maybeSweepCache`, marker prefixes `add` and `del`, and `markerData`.

Control flow: writes and deletes delegate to the underlying storage, then record cache markers for configured prefixes. Listing sweeps old markers, loads add/delete markers for the requested prefix, filters underlying provider results through delete markers, removes already-visible add markers, and fetches metadata for remaining recent additions.

State and persistence behavior: mutation markers are stored in the provided cache `blob.Storage` for `cacheDuration`; `nextSweepTime` is in-memory and mutex-protected.

Dependencies and integration points: used by repository blob layers where providers may be list-eventually-consistent.

Risks and test signals: marker write failures are intentionally ignored, and marker timestamp ordering decides add-vs-delete conflicts. Tests simulate eventual consistency, prefix filtering, deletion hiding, and sweeping expired markers.
