# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests_prep_localhost` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, `Install local dependencies for fstests command and control`, `Install junitparser`. Important modules/directives include `become`, `become_method`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`, `is_sle11sp1`, `is_sle11sp4`, `is_sle12`, `is_sle12sp1`, `is_sle12sp3`; plus 12 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
