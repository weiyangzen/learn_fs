<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-repo-format.sh -->
# sources/sync-backup/git-lfs/t/t-repo-format.sh

Purpose: checks that Git LFS commands do not silently operate in unsupported Git repository format versions.

Important APIs/functions: uses `git init`, direct `.git/config` mutation of repository format settings, and `git lfs env`.

Control flow: creates a repo, changes repository format metadata to an unsupported value, runs LFS command(s), and asserts the expected failure or diagnostic.

State and persistence: persists Git config keys in `.git/config`; no remote server state is required.

Dependencies and integration points: integrates with repository discovery, Git config parsing, and LFS environment initialization.

Risks: allowing unsupported repo formats can corrupt repositories or produce misleading behavior with newer Git storage/extensions.

Test signals: one focused repository-format test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-repo-format.sh -->
