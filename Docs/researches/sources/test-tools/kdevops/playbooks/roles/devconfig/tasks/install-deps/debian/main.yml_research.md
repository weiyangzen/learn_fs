# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Check if unattended-upgrades is installed`, `Set fact if unattended-upgrades is installed`, `Verify unattended-upgrades is not installed`, `Stop and disable unattended-upgrades related services`, `Update apt cache accepting release info changes`, `Upgrade Packages`, `Remove unattended-upgrades package in case upgrade installed it`, `Remove optional unattended-upgrades configuration files if they exist`, `Stop and disable unattended-upgrades related services`, `Allow for distro source change / upgrade`, `Check for UNAVAIL in /etc/nsswitch.conf hosts line`, `Write custom nsswitch.conf for hop1 mirror heuristic`; plus 13 more. Important modules/directives include `Acquire`, `apt`, `become`, `become_flags`, `become_method`, `changed_when`, `cmd`, `command`, `commands`, `content`, `copy`, `daemon_reload`; plus 43 more. Key variable inputs observed in this file include `item`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Check if unattended-upgrades is installed`, `Set fact if unattended-upgrades is installed`, `Verify unattended-upgrades is not installed`, `Stop and disable unattended-upgrades related services`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `systemd`. Notable path references include `/etc/apt/apt.conf.d/02periodic`, `/etc/apt/apt.conf.d/20auto-upgrades`, `/etc/apt/apt.conf.d/50unattended-upgrades`, `/etc/apt/apt.conf.d/52unattended-upgrades-local`, `/etc/apt/apt.conf.d/99ignore-release-date`, `/etc/nsswitch.conf`, `/etc/snmp/snmpd.conf`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `dpkg-query -W -f='${Status}' unattended-upgrades`, `cmd: apt-get update --allow-releaseinfo-change`, `apt-get update --allow-releaseinfo-change -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false -o Acquire::AllowInsecureRepositories=true`, `grep -E '^hosts:.*UNAVAIL' /etc/nsswitch.conf`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
