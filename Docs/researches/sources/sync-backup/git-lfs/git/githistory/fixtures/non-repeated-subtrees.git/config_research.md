# sources/sync-backup/git-lfs/git/githistory/fixtures/non-repeated-subtrees.git/config

Purpose: fixture config for history with unique subtree content, used to test callback ordering and path filters.

Important APIs/types/functions: standard non-bare `[core]` settings with reflog updates.

Control flow: none. The config enables normal Git object/ref access.

State/persistence behavior: temp-copy mutable repository metadata. No code runs from this file.

Dependencies/integration: used by tests for filtering `subdir/*.txt` and callback sequencing across root and child trees.

Risks/test signals: expected callback counts and filter behavior depend on fixture tree shape; config must remain compatible with local Git.
