# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we have figured out how to add repos for each`, `Disable things which require a repo to be set but that cannot be done`, `The default is to assume we are not on sle11 or sle10`, `Are we on SLE11 or SLE10?`, `The default is to assume all distros supports nvme-utils`, `Does this release lack nvme-utils`, `The default is to assume all distros supports git-core`, `Does this release lack git-core`, `Does this release use the package name git assume false`; plus 40 more. Important modules/directives include `backrefs`, `become`, `become_flags`, `become_method`, `check_mode`, `cmd`, `command`, `dest`, `enabled`, `fail`, `import_tasks`, `install_kdump`; plus 48 more. Includes/imports delegate to `update-grub/main.yml`. Key variable inputs observed in this file include `ansible_architecture`, `ansible_distribution_major_version`, `ansible_distribution_version`, `devconfig_repos_addon_list`, `item`, `kdump_high`, `kdump_low`, `role_path`, `suse_registration_code`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we have figured out how to add repos for each`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `lineinfile`, `systemd`. Notable path references include `/2.1/x86_64`, `/SLED`, `/etc/default/grub`, `/etc/snmp/snmpd.conf`, `/main.yml`, `/scripts/add-suse-repo-if-not-found.sh`, `/scripts/prepare_suse_repos.sh`, `/secret.yml`; plus 1 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `SUSEConnect -p sle-module-python2/{{ ansible_distribution_version }}/{{ ansible_architecture }}`, `cmd: "zypper in -y python-xml`, `kdumptool calibrate | grep ^High | awk '{print $2}'`, `kdumptool calibrate | grep ^Low | awk '{print $2}'`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
