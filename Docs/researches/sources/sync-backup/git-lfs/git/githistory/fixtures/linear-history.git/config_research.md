# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history.git/config

Purpose: base Git fixture config for simple linear commit history used by many rewriter tests.

Important APIs/types/functions: standard `[core]` config with repository format 0, `bare = false`, filemode and reflog enabled, plus case/unicode flags.

Control flow: no executable logic. It provides Git repository identity and behavior to subprocesses and `gitobj`.

State/persistence behavior: copied to temp before tests; rewritten commits and refs are created in the copy.

Dependencies/integration: used by rewriter tests for blob rewriting, additional tree entries, callbacks, ref updates, and fixture helpers.

Risks/test signals: test expected tree and commit SHAs depend on this fixture history exactly. If config makes the repo bare or changes Git behavior, `git update-ref` and `rev-parse` assertions can break.
