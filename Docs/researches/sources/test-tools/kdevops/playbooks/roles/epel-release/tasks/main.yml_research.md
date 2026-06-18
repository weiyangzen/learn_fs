# sources/test-tools/kdevops/playbooks/roles/epel-release/tasks/main.yml

## Purpose
Main task orchestration for the `epel-release` role, which enables EPEL package repositories on Red Hat family systems so later roles can install non-base dependencies. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Set epel-release package name for RHEL`, `Install the distribution's epel-release package`, `Enable the EPEL repository`. Important modules/directives include `argv`, `become`, `become_method`, `changed_when`, `command`, `delay`, `disable_gpg_check`, `dnf`, `epel_package`, `name`, `register`, `retries`; plus 3 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `epel_package`. The role-level integration surface is the `epel-release` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set epel-release package name for RHEL`, `Install the distribution's epel-release package`, `Enable the EPEL repository`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`. Notable path references include `//dl.fedoraproject.org/pub/epel/epel-release-latest-{{`, `/usr/bin/dnf`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated early in Red Hat provisioning. It feeds roles that need packages from EPEL and uses `dnf` plus `crb` enablement for newer distributions. Shell/command integration points observed here include `argv:`.

## Risks
The main risk is enabling the wrong repository set for the distribution release, especially CRB/EPEL differences across RHEL clones. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
