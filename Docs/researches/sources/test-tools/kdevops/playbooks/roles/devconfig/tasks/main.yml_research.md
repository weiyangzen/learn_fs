# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/main.yml

## Purpose
Main task orchestration for the `devconfig` role, which prepares kdevops test nodes for development and workflow execution by installing distribution packages, tuning boot/system services, propagating user configuration, and optionally revving kernels. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Wait for target nodes to become reachable`, `Gathering facts`, `Infer user on declared hosts`, `Infer group on declared hosts`, `Set inferred user and group for declared hosts`, `Ensure /etc/hostname is set`, `Check and fix APT mirrors for Debian testing`, `Install dependencies`, `Configure custom repositories and install packages`, `Configure en_US.UTF-8 locale files`, `Generate and update locales`; plus 54 more. Important modules/directives include `ansible.posix.sysctl`, `args`, `backrefs`, `become`, `become_flags`, `become_method`, `changed_when`, `check_mode`, `command`, `copy`, `create`, `daemon_reload`; plus 47 more. Includes/imports delegate to `check-apt-mirrors.yml`, `install-deps/main.yml`, `config-custom-repos-and-packages/main.yml`, `update-grub/main.yml`, `kotd-rev-kernel/main.yml`. Key variable inputs observed in this file include `ansible_default_ipv4`, `ansible_ssh_host`, `declared_host_group`, `declared_host_user`, `dev_bash_config`, `dev_bash_config_hacks_dest`, `dev_bash_config_hacks_generic`, `dev_bash_config_hacks_name`, `dev_bash_config_hacks_src`, `dev_bash_config_root`, `dev_gitconfig_dest`, `dev_gitconfig_src`, `devconfig_grub_console`, `devconfig_grub_timeout`; plus 10 more. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Wait for target nodes to become reachable`, `Gathering facts`, `Infer user on declared hosts`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `lineinfile`, `systemd`. Notable path references include `/.vimrc`, `/bin/bash`, `/dev/null`, `/etc/default/grub`, `/etc/default/grub.d/15_timeout.cfg`, `/etc/default/locale`, `/etc/hostname`, `/etc/locale.gen`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `whoami`, `id -g -n`, `|`, `git config --global --get-all safe.directory`, `git config --global --add safe.directory '*'`, `|`, `|`, `timedatectl set-ntp true`; plus 2 more.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
