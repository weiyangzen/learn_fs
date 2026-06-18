# sources/sync-backup/git-lfs/git/githistory/fixtures/packed-objects.git/config

Purpose: fixture config for a bare repository with packed objects, used to prove the rewriter and object database can visit packed blobs.

Important APIs/types/functions: `[core]` sets `bare = true` while otherwise using format 0, filemode, reflog, case, and unicode settings.

Control flow: no code. The `bare = true` value changes repository layout assumptions for Git and object lookup.

State/persistence behavior: fixture is copied to temp and opened as an object database; no working tree is expected.

Dependencies/integration: used by `TestRewriterVisitsPackedObjects`.

Risks/test signals: this config differs from the other fixtures; code paths relying on a worktree must not be assumed. If bare handling regresses, packed-object scanning may fail.
