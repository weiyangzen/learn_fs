<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-wildcards.sh -->
# sources/sync-backup/git-lfs/t/t-track-wildcards.sh

Purpose: validates leading-slash wildcard and filename pattern handling in `git lfs track`.

Important APIs/functions: uses `git lfs track`, `.gitattributes` comparison, file creation, add/commit, and `assert_pointer`.

Control flow: one case tracks wildcard patterns with a leading slash and confirms matching behavior; another tracks filename-style leading-slash patterns and verifies pointer conversion for expected files.

State and persistence: persists `.gitattributes`, working-tree files, index entries, and committed LFS pointers.

Dependencies and integration points: integrates with Git attributes pattern syntax, path normalization, and clean filter pointer generation.

Risks: leading slash and wildcard semantics are subtle; wrong escaping can track too much, too little, or produce unusable attributes.

Test signals: two tests cover wildcard and filename leading-slash variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-wildcards.sh -->
