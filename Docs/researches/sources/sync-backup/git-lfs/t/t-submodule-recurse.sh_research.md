<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-recurse.sh -->
# sources/sync-backup/git-lfs/t/t-submodule-recurse.sh

Purpose: ensures LFS operations behave correctly when Git's `submodule.recurse` option is enabled.

Important APIs/functions: uses remote/submodule setup helpers, `git config submodule.recurse true`, submodule commands, and LFS checkout/fetch behavior.

Control flow: builds a parent repo with an LFS-backed submodule, enables recurse behavior, and runs operations that would traverse submodules to verify LFS does not double-process or fail from unexpected working directories.

State and persistence: stores superproject config, submodule metadata, and submodule LFS objects.

Dependencies and integration points: integrates with Git recursive submodule behavior, repository discovery, and LFS hook/filter execution inside nested working trees.

Risks: global recursion can change command cwd and repository scope, which can break object paths or cause parent/submodule remotes to be confused.

Test signals: one focused recursive-submodule integration test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-recurse.sh -->
