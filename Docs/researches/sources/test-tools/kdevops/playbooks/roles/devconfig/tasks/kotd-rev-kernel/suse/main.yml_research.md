# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/suse/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we can add repos for a release`, `Disable things which require a repo to be set but that cannot be done`, `The default is to assume we are not on sle11 or sle10`, `Are we on SLE11 or SLE10?`, `Add extra addon repositories when enabled`, `Install kotd`, `Reboot into kotd`. Important modules/directives include `allow_vendor_change`, `become`, `become_method`, `cmd`, `disable_recommends`, `force`, `force_resolution`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`; plus 21 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`, `devconfig_kotd_repo`, `devconfig_kotd_repo_name`, `role_path`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we can add repos for a release`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`. Notable path references include `/scripts/add-suse-repo-if-not-found.sh`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
