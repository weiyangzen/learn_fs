# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/pull_images.yml

## Purpose
Main task orchestration for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure update script exists`, `Create update script if it doesn't exist`, `Ensure workflow images list exists`, `Create Docker images list if it doesn't exist`, `Run Docker mirror image preload script`, `Parse preload results`, `Display preload summary`, `Check for saved tarballs`, `Get tarball sizes`, `Display storage information`, `Check for failed images`, `Display warning if images failed`. Important modules/directives include `Location`, `Tarballs`, `async`, `become`, `changed_when`, `command`, `debug`, `dest`, `failed_when`, `http`, `mode`, `msg`; plus 11 more. Key variable inputs observed in this file include `docker_mirror_path`, `docker_mirror_port`, `failed_count`, `line`, `preload_result`, `tarball_count`, `tarball_size`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure update script exists`, `Create update script if it doesn't exist`, `Ensure workflow images list exists`, `Create Docker images list if it doesn't exist`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`. Notable path references include `//localhost`, `/dev/null`, `/images/workflow-images.txt`, `/logs/`, `/logs/update-`, `/mirror/docker`, `/registry/tarballs`, `/registry/tarballs/`; plus 1 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows. Shell/command integration points observed here include `{{ docker_mirror_path | default('/mirror/docker') }}/scripts/update-docker-images.sh`, `|`, `|`, `|`.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
