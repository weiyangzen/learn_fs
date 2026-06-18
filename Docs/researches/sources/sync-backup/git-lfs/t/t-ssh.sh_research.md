<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ssh.sh -->
# sources/sync-backup/git-lfs/t/t-ssh.sh

Purpose: verifies SSH endpoint support when `lfs.url` contains proxy-command syntax, both default and custom forms.

Important APIs/functions: uses `GIT_SSH`, `lfs-ssh-proxy-test`, `git lfs env`, `git lfs ls-files`, `git lfs fetch`, and LFS URL config.

Control flow: each case configures an SSH-style `lfs.url` with proxy command data, runs LFS commands, and checks that the custom SSH/proxy path is invoked correctly.

State and persistence: mutates repository-local LFS config and depends on the fake SSH command in the test environment; no long-lived remote state beyond the test repository.

Dependencies and integration points: integrates with SSH endpoint parsing, Git's SSH command environment, subprocess execution, and transfer adapter setup.

Risks: SSH URLs are quoting-sensitive; regressions can break proxy commands, mishandle spaces/options, or bypass configured transport.

Test signals: two cases cover default and custom proxy-command variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ssh.sh -->
