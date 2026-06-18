# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `docker-mirror` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install Docker dependencies on Debian`, `Install Docker dependencies on RedHat`, `Install Docker dependencies on SUSE`. Important modules/directives include `include_tasks`, `when`. Includes/imports delegate to `debian/main.yml`, `redhat/main.yml`, `suse/main.yml`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install Docker dependencies on Debian`, `Install Docker dependencies on RedHat`, `Install Docker dependencies on SUSE`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
