<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml

Source read: complete file, 6 lines, 155 bytes, sha256 `c22c6b8ca48c6f3f`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml_research.md`.

Purpose: defaults for selecting/enabling CodeReady Builder or equivalent repositories.

Important APIs/types/functions: `kdevops_enable_terraform` and `kdevops_enable_guestfs` default to false and are used by the task file to choose provider-specific RHEL repository names.

Control flow: no executable behavior.

State and persistence behavior: no direct state mutation; variables influence whether repository enablement commands run.

Dependencies and integration: supports `codereadyrepo/tasks/main.yml` and roles that need packages from CRB/CodeReady, notably guestfs or RHEL cloud provider images.

Risks: defaults may leave `codeready_repo` undefined for RedHat unless guestfs or terraform/provider flags are set.

Test signals: variable resolution tests for RedHat/AWS/Azure/GCE/CentOS/OracleLinux should select the intended repo string.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml -->
