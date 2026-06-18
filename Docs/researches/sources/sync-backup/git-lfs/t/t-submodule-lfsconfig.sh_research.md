<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh -->
# sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh

Purpose: verifies that `.lfsconfig` inside submodules is honored for environment reporting and submodule update/download behavior.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git submodule add/update`, `.lfsconfig`, `git lfs env`, and LFS object assertions.

Control flow: creates a submodule repository with LFS configuration, embeds it in a parent repo, and checks that LFS commands executed in the submodule use the configured endpoint. A second case updates submodules with `--init --remote` and verifies LFS content is fetched through `.lfsconfig`.

State and persistence: persists `.lfsconfig` in the submodule working tree/history and submodule metadata in the superproject.

Dependencies and integration points: integrates with Git submodules, per-repository LFS config discovery, endpoint resolution, and checkout/update hooks.

Risks: submodule config scope is easy to resolve incorrectly, causing downloads from the parent remote or failure to authenticate/fetch.

Test signals: two cases cover `git lfs env` and `git submodule update --init --remote` with `.lfsconfig`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh -->
