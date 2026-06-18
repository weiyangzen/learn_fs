# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-annotated-tags.git/config

Purpose: Git fixture config for a linear history containing annotated tags, used to validate tag-object rewriting during ref updates.

Important APIs/types/functions: standard `[core]` config with `bare = false`, reflog updates enabled, filemode true, and case/unicode settings.

Control flow: no logic. It lets Git commands resolve refs and tag objects in a copied fixture repository.

State/persistence behavior: non-bare repo metadata supports `git update-ref` during tests. The fixture is copied before use.

Dependencies/integration: used by `TestRefUpdaterMovesRefsWithAnnotatedTags`; the config must allow tag refs and object database access from `gitobj`.

Risks/test signals: annotated tag tests depend on this repository's tag object graph; config drift can invalidate expected SHA values.
