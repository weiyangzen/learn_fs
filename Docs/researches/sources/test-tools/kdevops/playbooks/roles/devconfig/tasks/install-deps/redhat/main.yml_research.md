# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Register system with Red Hat`, `Check whether custom repofile exists`, `Add custom yum repo`, `Discover the fastest package update mirrors`, `Increase the maximum number of concurrent package downloads`, `Refresh cache and upgrade all present packages`, `Reboot system to make the new kernel and modules take effect`, `Enable installation of packages from EPEL`, `Build install package list`, `Add btrfs-progs to install package list`, `Add GNU screen to install package list`, `Add Tmux to install package list`; plus 6 more. Important modules/directives include `activationkey`, `become`, `become_method`, `copy`, `delay`, `delegate_to`, `dest`, `dnf`, `enabled`, `force_register`, `group`, `include_role`; plus 24 more. Includes/imports delegate to `name: epel-release`. Key variable inputs observed in this file include `devconfig_custom_yum_repofile`, `packages`, `rhel_activation_key`, `rhel_org_id`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Register system with Red Hat`, `Check whether custom repofile exists`, `Add custom yum repo`, `Discover the fastest package update mirrors`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `lineinfile`, `systemd`. Notable path references include `/etc/dnf/dnf.conf`, `/etc/snmp/snmpd.conf`, `/etc/yum.repos.d/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
