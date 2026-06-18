# sources/sync-backup/kopia/repo/maintenance/pack_gc.go

Purpose: deletes pack and expired session blobs that are no longer referenced by the content index.

Important APIs/types/functions: `DeleteUnreferencedPacksOptions`, `DeleteUnreferencedPacks`, `ContentManager().IterateUnreferencedPacks`, `ListActiveSessions`, and `DeleteUnreferencedPacksStats`.

Control flow: default parallelism is set, delete workers are started unless dry-run, prefixes are selected, active sessions are loaded, cutoff time is determined with a one-second slack, and each unreferenced blob is retained or queued for deletion depending on timestamp, `PackDeleteMinAge`, and active-session checkpoint age.

State/persistence behavior: deletes unreferenced pack/session blobs from blob storage and reports unreferenced, retained, and deleted counts/sizes. It does not directly change content indexes.

Dependencies/integration: depends on direct repository writer, blob storage deletion, content manager unreferenced-pack iteration, session IDs, content logging, and stats counters.

Risks/test signals: deleting a still-needed pack is catastrophic, so timestamp and session retention checks are central. Tests cover referenced/unreferenced packs, dry-run-like retention behavior, and helper blob creation.
