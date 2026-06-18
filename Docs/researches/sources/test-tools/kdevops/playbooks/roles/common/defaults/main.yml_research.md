<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml

Source read: complete file, 7 lines, 168 bytes, sha256 `8325d12e9b10e149`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml_research.md`.

Purpose: defaults for the common kdevops role.

Important APIs/types/functions: `kdevops_data`, `kdevops_git`, and `kdevops_git_reset`.

Control flow: no direct tasks; the values control whether `common/tasks/main.yml` refreshes the kdevops checkout and where it lives.

State and persistence behavior: when reset is enabled, the checkout under `/data/kdevops` is created or updated from the configured repository.

Dependencies and integration: common role is included by data partition setup when UID/group inference is enabled and may be used by other roles needing shared user/group facts.

Risks: `kdevops_git_reset=false` means stale local checkout state is preserved by default. Enabling reset with `GIT_SSL_NO_VERIFY` in tasks weakens transport verification.

Test signals: default run should not modify the checkout; enabling reset should update `kdevops_data` from `kdevops_git`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml -->
