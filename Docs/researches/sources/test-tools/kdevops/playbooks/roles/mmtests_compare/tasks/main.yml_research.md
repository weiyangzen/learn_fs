# Research: sources/test-tools/kdevops/playbooks/roles/mmtests_compare/tasks/main.yml

`sources/test-tools/kdevops/playbooks/roles/mmtests_compare/tasks/main.yml` is a role task flow in the kdevops `mmtests_compare` role. Role context: compares mmtests benchmark result sets and generates HTML/graph reports. The file is 473 lines / 14997 bytes and was read in full for this report.

## Purpose

This Ansible file drives `mmtests_compare` role task flow behavior through 37 named task(s). The key task sequence is: `Install Perl dependencies for mmtests compare on localhost (Debian/Ubuntu)`, `Install additional Perl modules via CPAN on localhost (if needed)`, `Install Perl dependencies for mmtests compare on localhost (SUSE)`, `Install Perl dependencies for mmtests compare on localhost (RedHat/Fedora)`, `Create required directories`, `Clone mmtests repository locally`, `Check if mmtests fixes directory exists`, `Find mmtests patches in fixes directory`, `Apply mmtests patches if found`, `Get kernel versions from nodes`, plus 27 more.

## Important APIs, Types, And Functions

The primary Ansible interfaces are `MMTESTS_AUTO_PACKAGE_INSTALL`, `analysis_date`, `analysis_time`, `ansible.builtin.apt`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.dnf`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`, plus 41 more. Variables and facts referenced or defined include `analysis_date`, `analysis_time`, `ansible_date_time.date`, `ansible_date_time.time`, `basedir`, `baseline_hostname`, `baseline_kernel`, `baseline_kernel_version.stdout`, `become`, `become_method`, `benchmark_description`, `block`, `chdir`, `cmd`, `comparison_data`, `comparison_html_output.stdout`, `comparison_metrics`, `comparison_text_output.stdout`, plus 56 more. Registered result objects include `fixes_dir`, `mmtests_patches`, `patch_results`, `baseline_kernel_version`, `dev_kernel_version`, `comparison_text_output`, `comparison_html_output`, `iteration_files`, `graph_generation`, `graph_files`, plus 1 more. Included roles/tasks/templates or named dependencies visible in the file include none found.

## Control Flow

Execution follows Ansible task order. Conditional branches are controlled by `when` expressions, distribution selectors, feature flags, and registered command results. Notable conditions are `ansible_facts['os_family']|lower == 'debian'`, `ansible_facts['os_family']|lower == 'debian'`, `ansible_facts['os_family']|lower == 'suse'`, `ansible_facts['os_family']|lower == 'redhat'`, `fixes_dir.stat.exists`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `kdevops_baseline_and_dev|bool`, `name: Check for available iterations data`, plus 9 more. The file also uses Ansible `block` structure for grouped operations and, where present, rescue/error-recovery behavior. Loops expand repeated package, host, disk, result, or service operations over inventory or variable-provided lists.

## State And Persistence

Persistent effects visible from this file target `{{ topdir_path }}/tmp/mmtests`, `/tmp/baseline-mmtests-results.tar.gz`, `/tmp/dev-mmtests-results.tar.gz`, `{{ topdir_path }}/tmp/`, `{{ topdir_path }}/tmp/`, `{{ topdir_path }}/tmp/mmtests/work/log/`, `{{ topdir_path }}/tmp/mmtests/work/log/`, `{{ item.path | dirname }}`, `{{ topdir_path }}/workflows/mmtests/results/compare/comparison_report.html`, `{{ item.dest }}`, `{{ topdir_path }}/workflows/mmtests/results/compare/comparison.txt`, `{{ topdir_path }}/workflows/mmtests/results/compare/comparison_raw.html`, `{{ topdir_path }}/workflows/mmtests/results/{{ item.split(`, `{{ item }}`, `{{ topdir_path }}/workflows/mmtests/fixes/`, `{{ topdir_path }}/tmp/mmtests/work/log/{{ item }}`, plus 19 more. State changes are delegated to Ansible modules, so idempotency depends on module semantics, `creates` guards, `changed_when`, `failed_when`, and the external commands used. Facts set with `set_fact` live for the current play and feed later role tasks; files, packages, services, mounts, libvirt resources, certificates, and benchmark outputs persist on the controller or managed hosts as directed by each task.

## Dependencies And Integration Points

The file integrates with role `mmtests_compare`, inventory variables, Ansible facts, optional `extra_vars` files, and the kdevops top-level paths such as `topdir_path` when referenced. External integration points inferred from modules and commands include `MMTESTS_AUTO_PACKAGE_INSTALL`, `analysis_date`, `analysis_time`, `ansible.builtin.apt`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.dnf`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`, `ansible.builtin.stat`, `ansible.builtin.template`, `ansible.builtin.unarchive`, `ansible.posix.patch`, plus 37 more. For install-deps files, package manager behavior is distribution-specific and selected by the parent include file.

## Risks And Edge Cases

command/shell tasks can be non-idempotent unless guarded by `creates`, return-code checks, or explicit changed/failed conditions; privileged operations depend on sudo/root access and can leave host-level state behind; ignored failures can hide missing optional inputs or partial setup; controller-local paths and permissions must match the invoking user; incorrect feature flags or distribution facts can skip required setup.

## Test Signals

Useful validation signals are Ansible syntax-check for this role, running the role with `--check` where modules support it, and exercising the feature tags/conditions that import this file. Runtime confirmation should inspect registered results, created files/directories, package/service state, and any debug/status tasks emitted by the role.
