<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule.sh -->
# sources/sync-backup/git-lfs/t/t-submodule.sh

Purpose: verifies baseline LFS behavior in Git submodules, including local gitdir layout and environment reporting.

Important APIs/functions: uses `git submodule add`, `git lfs env`, `setup_remote_repo_with_file`, and repository path helpers.

Control flow: creates submodule repositories containing LFS files, embeds them in parent repos, then inspects local Git directory resolution and LFS environment output from inside the submodule.

State and persistence: creates `.git/modules/...` submodule gitdirs, working-tree gitfile pointers, and local LFS config/media state.

Dependencies and integration points: integrates with Git's submodule gitdir indirection, LFS local storage discovery, and environment command output.

Risks: wrong gitdir resolution can store media in the parent repository, break hooks, or report incorrect endpoints for nested repos.

Test signals: two cases cover submodule local git directory behavior and `git lfs env`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule.sh -->
