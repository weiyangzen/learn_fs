# sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/defaults/main.yml

## Purpose
Defines default variables for the `docker_mirror_9p` role, which mounts a host-side Docker mirror directory into guests over 9P for shared image-cache access. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `docker_mirror_9p` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated with guest definitions that expose a 9P tag. It depends on host directory creation, a guest mount point, Linux 9P support, and the `docker_mirror_9p_*` variables.

## Risks
The main risks are missing guest 9P support, stale host mount contents, and treating a mountpoint check as sufficient proof that image data is usable. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; verify block-device and mount topology before and after the run.
