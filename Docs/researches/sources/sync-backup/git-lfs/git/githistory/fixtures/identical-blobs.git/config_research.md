# sources/sync-backup/git-lfs/git/githistory/fixtures/identical-blobs.git/config

Purpose: Git fixture config for a non-bare repository where two paths can reference identical blob contents. It supports rewriter tests that prove caching is keyed by path plus object ID, not only object ID.

Important APIs/types/functions: standard `[core]` keys: `repositoryformatversion = 0`, `filemode = true`, `bare = false`, `logallrefupdates = true`, `ignorecase = true`, and `precomposeunicode = true`.

Control flow: no executable logic. Git and `gitobj` consume this config when the fixture is copied to a temp directory and opened.

State/persistence behavior: declares the fixture as mutable, non-bare working repository metadata with reflog updates. Test helpers copy it before mutation so the original fixture remains unchanged.

Dependencies/integration: consumed by `DatabaseFromFixture` and `TestRewriterVisitsUniqueEntriesWithIdenticalContents`.

Risks/test signals: fixture config is minimal and platform-tuned for macOS-like case/unicode settings. If `bare` or object paths change, rewriter tests may fail to locate refs or objects.
