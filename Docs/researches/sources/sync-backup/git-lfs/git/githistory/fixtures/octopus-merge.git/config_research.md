# sources/sync-backup/git-lfs/git/githistory/fixtures/octopus-merge.git/config

Purpose: fixture config for an octopus merge history used to validate parent rewriting across multi-parent commits.

Important APIs/types/functions: standard `[core]` config for a non-bare repository.

Control flow: no direct logic. The rewriter reads commits/trees and writes rewritten objects in a temp copy.

State/persistence behavior: supports reflog updates and mutable refs in tests.

Dependencies/integration: used by `TestRewriterRewritesOctopusMerges`.

Risks/test signals: if fixture ancestry changes, expected parent SHAs and tree IDs in the test become invalid.
