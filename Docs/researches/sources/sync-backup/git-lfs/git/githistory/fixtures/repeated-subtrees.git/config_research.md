# sources/sync-backup/git-lfs/git/githistory/fixtures/repeated-subtrees.git/config

Purpose: fixture config for a history with repeated subtree/object entries, used to validate rewriter caching and avoiding unnecessary revisits.

Important APIs/types/functions: standard non-bare `[core]` repository config.

Control flow: no executable behavior. Git commands and `gitobj` consume it from a temp copy.

State/persistence behavior: temp-copy repository state can be rewritten without affecting the source fixture.

Dependencies/integration: used by `TestRewriterDoesntVisitUnchangedSubtrees`.

Risks/test signals: expected visit counts depend on this fixture's repeated subtree structure and on the repo remaining non-bare.
