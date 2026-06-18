# sources/sync-backup/restic/cmd/restic/exclude.go

Purpose: provides a reject filter that excludes restic's cache directory from archiving.

Important APIs/types/functions: `rejectResticCache(repo *repository.Repository)`.

Control flow and state: if repository cache is nil, returns a function that never rejects. Otherwise it reads `repo.Cache().BaseDir`, errors if empty, and returns a predicate that rejects items having the cache base as a path prefix while logging the rejection.

Dependencies and integration points: uses archiver reject function type, repository cache, `fs.HasPathPrefix`, debug logging, and restic errors.

Risks: path-prefix direction must remain correct to avoid backing up cache contents or rejecting unrelated paths. Empty cache base is treated as an error to avoid matching everything.

Test signals: no direct tests in this shard; backup behavior likely exercises it.
