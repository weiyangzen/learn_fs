# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Gather os_family`, `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Debian-specific setup`, `SuSE-specific setup`, `Red Hat-specific setup`. Important modules/directives include `gather_subset`, `ignore_errors`, `include_tasks`, `include_vars`, `setup`, `skip`, `tags`, `when`, `with_first_found`. Includes/imports delegate to `debian/main.yml`, `suse/main.yml`, `redhat/main.yml`. Key variable inputs observed in this file include `ansible_facts`, `item`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Gather os_family`, `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Debian-specific setup`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
