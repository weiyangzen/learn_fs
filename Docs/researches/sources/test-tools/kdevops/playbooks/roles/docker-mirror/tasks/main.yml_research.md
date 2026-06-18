# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/main.yml

## Purpose
Main task orchestration for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Check if Docker mirror directory exists`, `Check if Docker is installed`, `Install Docker dependencies`, `Create Docker mirror directory structure`, `Create Docker registry configuration`, `Check if Docker registry container is running`, `Pull registry image`, `Start Docker registry mirror container`, `Wait for registry to be ready`, `Display Docker mirror status`, `Create Docker images list from workflows`, `Create README in images directory to clarify its purpose`; plus 8 more. Important modules/directives include `become`, `changed_when`, `command`, `daemon_reload`, `debug`, `delay`, `dest`, `enabled`, `failed_when`, `file`, `ignore_errors`, `include_tasks`; plus 19 more. Includes/imports delegate to `install-deps/main.yml`, `pull_images.yml`. Key variable inputs observed in this file include `docker_mirror_dir`, `docker_mirror_path`, `docker_mirror_port`, `item`, `registry_status`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Check if Docker mirror directory exists`, `Check if Docker is installed`, `Install Docker dependencies`, `Create Docker mirror directory structure`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `template`, `file`, `systemd`. Notable path references include `//localhost`, `//registry-1.docker.io`, `/config`, `/config/config.yml`, `/etc/docker/registry/config.yml`, `/etc/systemd/system/docker-mirror-update.service`, `/etc/systemd/system/docker-mirror-update.timer`, `/images`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows. Shell/command integration points observed here include `docker --version`, `docker ps -f name=kdevops-docker-mirror --format "{{ '{{' }}.Status{{ '}}' }}`, `docker pull registry:2`, `|`.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
