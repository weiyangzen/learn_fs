# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Set the path where we collect our kotd updates`, `Get used target kernel version prior to reving kernel`, `Document used target kernel version prior to reving kernel`, `Distribution specific setup`, `Check kernel uname`, `Get used target kernel version after reving kernel`, `Document used target kernel version after reving kernel`. Important modules/directives include `command`, `debug`, `delegate_to`, `ignore_errors`, `import_tasks`, `include_vars`, `kotd_uname_after`, `kotd_uname_before`, `msg`, `register`, `run_once`, `running_kernel`; plus 7 more. Includes/imports delegate to `debian/main.yml`, `suse/main.yml`, `redhat/main.yml`. Key variable inputs observed in this file include `ansible_facts`, `item`, `kotd_uname_after`, `kotd_uname_before`, `running_kernel`, `uname_cmd`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Set the path where we collect our kotd updates`, `Get used target kernel version prior to reving kernel`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`. Notable path references include `/.kotd.uname-after.txt`, `/.kotd.uname-before.txt`, `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `uname -r`, `echo {{ uname_cmd.stdout_lines | regex_replace('\]') | regex_replace('\[') }} > {{ kotd_uname_before }}`, `uname -r`, `echo {{ uname_cmd.stdout_lines | regex_replace('\]') | regex_replace('\[') }} > {{ kotd_uname_after }}`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
