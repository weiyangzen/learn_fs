# sources/test-tools/kdevops/playbooks/roles/docker-mirror/defaults/main.yml

## Purpose
Defines default variables for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
