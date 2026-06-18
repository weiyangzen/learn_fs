<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml

Source read: complete file, 67 lines, 2501 bytes, sha256 `a77ad52f458a5afc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml_research.md`.

Purpose: enable the correct CodeReady Builder, CRB, or cloud RHUI repository for non-Fedora RedHat-like systems unless a custom yum repo file is configured.

Important APIs/types/functions: `set_fact codeready_repo`, `ansible.builtin.fail`, and `ansible.builtin.command` invoking `/usr/bin/dnf config-manager --enable {{ codeready_repo }}`.

Control flow: skip Fedora and custom yum repofile hosts; choose repo name for RedHat+guestfs, OracleLinux, CentOS, RedHat+terraform AWS/Azure/GCE; fail if no heuristic matches; enable selected repo and mark changed on success.

State and persistence behavior: mutates dnf repository enablement on the target. The selected repo name persists as an Ansible fact for the play.

Dependencies and integration: relies on `devconfig_custom_yum_repofile`, distribution facts, terraform provider variables, and dnf config-manager availability. It enables packages needed by other roles.

Risks: RedHat without guestfs or recognized terraform provider fails. `devconfig_custom_yum_repofile` must be defined or defaulted elsewhere. Repo names are provider/version/architecture sensitive.

Test signals: matrix dry runs across RedHat bare, AWS, Azure, GCE, CentOS, OracleLinux, and Fedora should show the expected enable or skip/fail behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml -->
