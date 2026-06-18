# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure required /media/ directories are created`, `Oscheck distribution ospecific setup`. Important modules/directives include `become`, `become_method`, `file`, `import_tasks`, `name`, `path`, `state`, `when`, `with_items`. Includes/imports delegate to `name: pkg`, `tasks/install-deps/debian/main.yml`, `tasks/install-deps/suse/main.yml`, `tasks/install-deps/redhat/main.yml`. Key variable inputs observed in this file include `item`, `sparsefiles_path`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure required /media/ directories are created`, `Oscheck distribution ospecific setup`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `file`. Notable path references include `/install-deps/debian/main.yml`, `/install-deps/redhat/main.yml`, `/install-deps/suse/main.yml`, `/media/`, `/media/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
