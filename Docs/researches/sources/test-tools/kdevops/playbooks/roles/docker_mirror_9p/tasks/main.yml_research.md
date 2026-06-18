# sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/tasks/main.yml

## Purpose
Main task orchestration for the `docker_mirror_9p` role, which mounts a host-side Docker mirror directory into guests over 9P for shared image-cache access. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure Docker mirror 9P host directory exists`, `Create Docker mirror 9P guest mount point`, `Mount Docker mirror 9P filesystem in guest`, `Verify Docker mirror 9P mount is active`. Important modules/directives include `changed_when`, `command`, `delegate_to`, `failed_when`, `file`, `fstype`, `mode`, `mount`, `opts`, `path`, `register`, `run_once`; plus 4 more. Key variable inputs observed in this file include `docker_mirror_9p_guest_mount_point`, `docker_mirror_9p_host_path`, `docker_mirror_9p_mount_tag`. The role-level integration surface is the `docker_mirror_9p` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure Docker mirror 9P host directory exists`, `Create Docker mirror 9P guest mount point`, `Mount Docker mirror 9P filesystem in guest`, `Verify Docker mirror 9P mount is active`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `file`, `mount`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with guest definitions that expose a 9P tag. It depends on host directory creation, a guest mount point, Linux 9P support, and the `docker_mirror_9p_*` variables. Shell/command integration points observed here include `mountpoint -q "{{ docker_mirror_9p_guest_mount_point }}`.

## Risks
The main risks are missing guest 9P support, stale host mount contents, and treating a mountpoint check as sufficient proof that image data is usable. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; verify block-device and mount topology before and after the run.
