# sources/sync-backup/kopia/repo/content/content_manager_indexes.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_indexes.go_research.md`.

Purpose: exposes operations around committed content index blobs: refreshing local index views, compacting index blobs, and parsing an encrypted index blob into `Info` entries.

Important APIs: `SharedManager.Refresh` invalidates the index blob manager cache and reloads pack indexes under `indexesLock`. `SharedManager.CompactIndexes` calls the active index blob manager's compaction operation, then reloads committed indexes while holding the same lock to avoid races with refresh. `ParseIndexBlob` decrypts a provided encrypted index blob and opens it with the generic `index.Open` reader.

Control flow and integration: refresh obtains the active `indexblob.Manager`, invalidates its cached active-list view, then calls `loadPackIndexesLocked`. Compaction logs options, asks the manager to compact active index blobs, and reloads the merged committed index set afterward. `ParseIndexBlob` is a utility path: decrypt into a `gather.WriteBuffer`, open the index using encryptor overhead for v1 original-length reconstruction, iterate all IDs, and collect results.

State and persistence behavior: these functions do not directly change pack data. `Refresh` and compaction mutate the in-memory committed-content index view; compaction can create replacement index blobs and supersede old ones through the index blob manager.

Dependencies: `blobcrypto`, `indexblob`, `maintenancestats`, `timetrack`, content logging, `blob.ID`, and `index`.

Risks and tests: the main risk is stale or racy index views after compaction; the explicit `indexesLock` guards that. `ParseIndexBlob` propagates decrypt/open/iteration failures. Content manager tests cover refresh visibility, compaction, permissive index loading, and index recovery interactions.
