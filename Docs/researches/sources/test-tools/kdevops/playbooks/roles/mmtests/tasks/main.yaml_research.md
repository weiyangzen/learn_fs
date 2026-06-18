# Research: sources/test-tools/kdevops/playbooks/roles/mmtests/tasks/main.yaml

`sources/test-tools/kdevops/playbooks/roles/mmtests/tasks/main.yaml` is a role task flow in the kdevops `mmtests` role. Role context: installs, configures, and runs mmtests memory-management benchmarks. The file is 339 lines / 10206 bytes and was read in full for this report.

## Purpose

This Ansible file drives `mmtests` role task flow behavior through 34 named task(s). The key task sequence is: `Install dependencies`, `Ensure data_dir has correct ownership`, `Clone mmtests repository`, `Check if mmtests fixes directory exists`, `Find mmtests patches in fixes directory`, `Copy patches to remote host`, `Apply mmtests patches on remote host`, `Report patch application results`, `Generate mmtests configuration`, `Fail if configured memory percentages overcommit available memory`, plus 24 more.

## Important APIs, Types, And Functions

The primary Ansible interfaces are `Stderr`, `Stdout`, `ansible.builtin.async_status`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.fail`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.include_tasks`, `ansible.builtin.shell`, `ansible.builtin.stat`, plus 19 more. Variables and facts referenced or defined include `Stderr`, `Stdout`, `args`, `async`, `become`, `become_method`, `changed_when`, `data_group`, `data_path`, `data_user`, `delay`, `delegate_to`, `dest`, `failed_when`, `flat`, `force`, `group`, `ignore_errors`, plus 43 more. Registered result objects include `fixes_dir`, `mmtests_patches`, `patch_results`, `kernel_version`, `mmtests_build_result`, `mountpoint_stat`, `mmtests_job`, `mmtests_status`. Included roles/tasks/templates or named dependencies visible in the file include `common`, `create_data_partition`.

## Control Flow

Execution follows Ansible task order. Conditional branches are controlled by `when` expressions, distribution selectors, feature flags, and registered command results. Notable conditions are `fixes_dir.stat.exists`, `(mmtests_anonymous_memory_percent + mmtests_file_memory_percent) > 100`, `mmtests_build_result.rc != 0`, `mmtests_requires_mkfs_device | bool`, `mmtests_pretest_dropvmcaches | bool`. Loops expand repeated package, host, disk, result, or service operations over inventory or variable-provided lists.

## State And Persistence

Persistent effects visible from this file target `{{ mmtests_data_dir }}`, `/tmp/{{ item.path | basename }}`, `{{ mmtests_data_dir }}/configs/config-workload-{{ mmtests_test_type }}-kdevops`, `{{ topdir_path }}/workflows/mmtests/results/{{ inventory_hostname }}/`, `{{ topdir_path }}/workflows/mmtests/results/{{ inventory_hostname }}/mmtests-results-{{ inventory_hostname }}`, `{{ data_path }}`, `{{ topdir_path }}/workflows/mmtests/fixes/`, `{{ topdir_path }}/workflows/mmtests/results/{{ inventory_hostname }}/`, `{{ mmtests_results_dir_basename }}/mmtests-results-{{ inventory_hostname }}.tar.gz`, `{{ item }}`, `{{ topdir_path }}/workflows/mmtests/results/{{ inventory_hostname }}/mmtests-results-{{ inventory_hostname }}`, `{{ item }}`, `{{ item }}`, `{{ item.path }}`, `{{ mmtests_test_type }}-config.j2`, `{{ mmtests_results_dir_basename }}/mmtests-results-{{ inventory_hostname }}.tar.gz`, plus 6 more. State changes are delegated to Ansible modules, so idempotency depends on module semantics, `creates` guards, `changed_when`, `failed_when`, and the external commands used. Facts set with `set_fact` live for the current play and feed later role tasks; files, packages, services, mounts, libvirt resources, certificates, and benchmark outputs persist on the controller or managed hosts as directed by each task.

## Dependencies And Integration Points

The file integrates with role `mmtests`, inventory variables, Ansible facts, optional `extra_vars` files, and the kdevops top-level paths such as `topdir_path` when referenced. External integration points inferred from modules and commands include `Stderr`, `Stdout`, `ansible.builtin.async_status`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.fail`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.include_tasks`, `ansible.builtin.shell`, `ansible.builtin.stat`, `ansible.builtin.template`, `ansible.builtin.unarchive`, `chdir`, `creates`, plus 17 more. For install-deps files, package manager behavior is distribution-specific and selected by the parent include file.

## Risks And Edge Cases

command/shell tasks can be non-idempotent unless guarded by `creates`, return-code checks, or explicit changed/failed conditions; privileged operations depend on sudo/root access and can leave host-level state behind; ignored failures can hide missing optional inputs or partial setup; controller-local paths and permissions must match the invoking user; incorrect feature flags or distribution facts can skip required setup.

## Test Signals

Useful validation signals are Ansible syntax-check for this role, running the role with `--check` where modules support it, and exercising the feature tags/conditions that import this file. Runtime confirmation should inspect registered results, created files/directories, package/service state, and any debug/status tasks emitted by the role.
