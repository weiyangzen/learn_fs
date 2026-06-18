# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/redhat/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Add KOTD repository`, `Parse repository id from repo file`, `Get kernel version from repository-packages`, `Install KOTD`, `Reboot system to make the new kernel and modules take effect`. Important modules/directives include `arch`, `become`, `become_method`, `changed_when`, `dest`, `disable_gpg_check`, `dnf`, `get_url`, `kernel_version`, `name`, `reboot`, `register`; plus 9 more. Key variable inputs observed in this file include `arch`, `devconfig_kotd_repo`, `kernel_version`, `repo_file`, `repo_id`, `result`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Add KOTD repository`, `Parse repository id from repo file`, `Get kernel version from repository-packages`, `Install KOTD`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `file`. Notable path references include `/etc/yum.repos.d`, `/etc/yum.repos.d/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `grep -E '\[.*\]' /etc/yum.repos.d/{{ repo_file }} | tr -d '[]'`, `dnf -q --repo={{ repo_id }} repoquery --qf "%{version}-%{release}" kernel.x86_64`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
