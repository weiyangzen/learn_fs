# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-tags.git/config

Purpose: Git fixture config for a linear history with lightweight tags, used for partial migration and ref update tests.

Important APIs/types/functions: standard `[core]` keys with `bare = false`, `logallrefupdates = true`, `filemode = true`, `ignorecase = true`, and `precomposeunicode = true`.

Control flow: no code; Git reads the config when resolving tags and commit ancestry.

State/persistence behavior: copied fixture can have refs updated in temp state without touching source fixture.

Dependencies/integration: supports `TestHistoryRewriterUseOriginalParentsForPartialMigration`, `TestRefUpdaterMovesRefs`, and `TestRefUpdaterIgnoresUnovedRefs`.

Risks/test signals: expected commit/tag SHAs in tests are tightly coupled to the fixture contents and config being a normal repository.
