# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/main.yaml

## Purpose
Main task orchestration for the `fio-tests` role, which formats or mounts test storage, generates fio job files, runs fio workloads, and collects result archives. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Install dependencies`, `Ensure data_dir has correct ownership`, `Resolve per-host filesystem configuration`, `Set filesystem-specific mkfs and mount options`, `Set derived configuration variables`, `Check if {{ fio_tests_fs_device }} is mounted`, `Unmount {{ fio_tests_fs_device }} if mounted`, `Create filesystem on {{ fio_tests_fs_device }}`, `Create mount point directory`, `Mount filesystem`, `Set filesystem mount ownership`, `Create results directory`; plus 23 more. Important modules/directives include `Result`, `args`, `async`, `async_status`, `become`, `become_method`, `block_size`, `changed_when`, `command`, `creates`, `debug`, `delay`; plus 59 more. Includes/imports delegate to `install-deps/main.yml`, `name: create_data_partition`, `name: common`. Key variable inputs observed in this file include `data_group`, `data_path`, `data_user`, `fio_job`, `fio_tests_block_ranges`, `fio_tests_block_sizes`, `fio_tests_device`, `fio_tests_effective_block_sizes`, `fio_tests_enable_bs_ranges`, `fio_tests_fs_device`, `fio_tests_fs_label`, `fio_tests_fs_mount_point`, `fio_tests_fs_type`, `fio_tests_io_depths`; plus 12 more. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install dependencies`, `Ensure data_dir has correct ownership`, `Resolve per-host filesystem configuration`, `Set filesystem-specific mkfs and mount options`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `fetch`, `mount`. Notable path references include `/bw_`, `/cpufreq/scaling_governor`, `/dev/disk/by-id/virtio-kdevops2`, `/dev/null`, `/fio-tests-results-{{`, `/iops_`, `/jobs`, `/jobs/`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories. Shell/command integration points observed here include `findmnt --noheadings --output TARGET --source {{ fio_tests_fs_device }}`, `umount {{ fio_tests_fs_device }}`, `>`, `uname -r`, `|`, `|`, `ls {{ fio_tests_results_dir }}/jobs/*.ini 2>/dev/null | wc -l`, `|`; plus 1 more.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; result collection can silently miss files when paths or host-derived names differ.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; verify block-device and mount topology before and after the run.
