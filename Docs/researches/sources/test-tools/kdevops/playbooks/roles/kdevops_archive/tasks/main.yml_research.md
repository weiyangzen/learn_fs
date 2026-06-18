# Research: sources/test-tools/kdevops/playbooks/roles/kdevops_archive/tasks/main.yml

`sources/test-tools/kdevops/playbooks/roles/kdevops_archive/tasks/main.yml` is a role task flow in the kdevops `kdevops_archive` role. Role context: archives kdevops workflow outputs and system state. The file is 491 lines / 15943 bytes and was read in full for this report.

## Purpose

This Ansible file drives `kdevops_archive` role task flow behavior through 76 named task(s). The key task sequence is: `Install git-lfs`, `Override kdevops archive repo url to demo URL if in demo mode`, `Notify this is a kdevops-results-archive demo`, `Check if kdevops archive/ directory exists`, `Remove stale kdevops archive/ directory`, `Create new kdevops archive/ for new results`, `Get list of files from make ci-results for our archive/`, `Get current user`, `Ensure source files are readable by current user`, `Copy files and directories to the our archive/`, plus 66 more.

## Important APIs, Types, And Functions

The primary Ansible interfaces are `GIT_LFS_FORCE`, `GIT_LFS_SKIP_SMUDGE`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.meta`, `ansible.builtin.package`, `ansible.builtin.set_fact`, `ansible.builtin.shell`, `ansible.builtin.slurp`, `ansible.builtin.stat`, plus 46 more. Variables and facts referenced or defined include `'%04d' % (next_number_int`, `'%Y%m%d'`, `(current_highest`, `(item.stat.size / 1024 / 1024)`, `(kdevops_archive_test_subject`, `(numbered_dirs`, `GIT_LFS_FORCE`, `all_dirs.files`, `archive_files.files`, `archive_stats.results`, `args`, `become`, `become_flags`, `become_method`, `changed_when`, `ci_commit_content.content`, `ci_commit_enhanced_content.content`, `ci_ref_content.content`, plus 67 more. Registered result objects include `results_dir`, `ci_results`, `current_user`, `kdevops_archive_data`, `ci_ref_file`, `ci_ref_content`, `archive_files`, `archive_stats`, `archive_dir`, `mirror_dir`, plus 14 more. Included roles/tasks/templates or named dependencies visible in the file include none found.

## Control Flow

Execution follows Ansible task order. Conditional branches are controlled by `when` expressions, distribution selectors, feature flags, and registered command results. Notable conditions are `results_dir.stat.exists`, `ci_results.stdout_lines | length > 0`, `ci_results.stdout_lines | length > 0`, `ci_results.stdout_lines | length > 0`, `ci_ref_file.stat.exists`, `ci_ref_file.stat.exists`, `not ci_ref_file.stat.exists`, `ci_trigger_file.stat.exists`, `ci_trigger_file.stat.exists`, `not ci_trigger_file.stat.exists`, `ci_subject_file.stat.exists`, `ci_subject_file.stat.exists`, `not ci_subject_file.stat.exists`, `ci_commit_file.stat.exists`, plus 9 more. Loops expand repeated package, host, disk, result, or service operations over inventory or variable-provided lists.

## State And Persistence

Persistent effects visible from this file target `{{ kdevops_results }}/{{ kdevops_archive_test_ref }}.xz`, `{{ kdevops_results }}/{{ kdevops_archive_test_ref }}.zip`, `{{ kdevops_results_archive_dir }}`, `{{ kdevops_results_archive_dir }}/{{ kdevops_archive_prefix }}`, `{{ kdevops_results_archive_dir }}/{{ kdevops_archive_prefix }}/{{ kdevops_archive_test_ref }}.tar.xz`, `{{ tmp_commit_msg.path }}`, `{{ kdevops_results_local }}`, `{{ kdevops_results_local }}`, `{{ kdevops_results_local }}`, `{{ topdir_path }}/ci.ref`, `{{ topdir_path }}/ci.ref`, `{{ kdevops_results_local }}`, `{{ kdevops_results_local }}`, `{{ item.path }}`, `{{ kdevops_results_archive_dir }}`, `{{ kdevops_archive }}`, plus 23 more. State changes are delegated to Ansible modules, so idempotency depends on module semantics, `creates` guards, `changed_when`, `failed_when`, and the external commands used. Facts set with `set_fact` live for the current play and feed later role tasks; files, packages, services, mounts, libvirt resources, certificates, and benchmark outputs persist on the controller or managed hosts as directed by each task.

## Dependencies And Integration Points

The file integrates with role `kdevops_archive`, inventory variables, Ansible facts, optional `extra_vars` files, and the kdevops top-level paths such as `topdir_path` when referenced. External integration points inferred from modules and commands include `GIT_LFS_FORCE`, `GIT_LFS_SKIP_SMUDGE`, `ansible.builtin.command`, `ansible.builtin.copy`, `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.git`, `ansible.builtin.meta`, `ansible.builtin.package`, `ansible.builtin.set_fact`, `ansible.builtin.shell`, `ansible.builtin.slurp`, `ansible.builtin.stat`, `ansible.builtin.tempfile`, `chdir`, `cmd`, `commit_message`, plus 42 more. For install-deps files, package manager behavior is distribution-specific and selected by the parent include file.

## Risks And Edge Cases

command/shell tasks can be non-idempotent unless guarded by `creates`, return-code checks, or explicit changed/failed conditions; privileged operations depend on sudo/root access and can leave host-level state behind; ignored failures can hide missing optional inputs or partial setup; incorrect feature flags or distribution facts can skip required setup.

## Test Signals

Useful validation signals are Ansible syntax-check for this role, running the role with `--check` where modules support it, and exercising the feature tags/conditions that import this file. Runtime confirmation should inspect registered results, created files/directories, package/service state, and any debug/status tasks emitted by the role.
