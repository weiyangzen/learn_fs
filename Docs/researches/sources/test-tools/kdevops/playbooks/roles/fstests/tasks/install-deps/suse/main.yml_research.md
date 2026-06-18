# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, `The default is to assume all distros have the indent package`, `Does this release lack indent`, `The default is to assume all distros supports nvme-utils`, `Does this release lack nvme-utils`, `Install nvme tools`, `Install build dependencies for fstests`, `Install indent when we have it`; plus 13 more. Important modules/directives include `add_benchmark_repo`, `badname_arg`, `become`, `become_method`, `cmd`, `enabled`, `has_indent`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`; plus 20 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`, `role_path`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `By default we assume we have figured out how to add repos on a release`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `systemd`. Notable path references include `//download.opensuse.org/repositories/benchmark/SLE_12_SP5/`, `//download.opensuse.org/repositories/benchmark/SLE_15_SP2/`, `//download.opensuse.org/repositories/benchmark/SLE_15_SP3/`, `/scripts/add-suse-repo-if-not-found.sh`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; check target systemd unit state after the role; verify block-device and mount topology before and after the run.
