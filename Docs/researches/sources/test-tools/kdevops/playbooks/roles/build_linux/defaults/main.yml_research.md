<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml

Source read: complete file, 26 lines, 1007 bytes, sha256 `e9b3d0f5e2a2eba4`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml_research.md`.

Purpose: defaults for the build-linux workflow role, controlling repeated kernel build benchmarking and optional dedicated build storage.

Important APIs/types/functions: variables include `build_linux_repeat_count`, `build_linux_make_jobs`, `build_linux_target`, `build_linux_clean_between`, `build_linux_collect_stats`, `build_linux_results_dir`, `build_linux_storage_enable`, `build_linux_device`, `build_linux_use_latest_tag`, `build_linux_allow_modifications`, `shallow_clone`, `clone_depth`, `linux_source_dir`, `linux_build_dir`, and `linux_git_url`.

Control flow: no executable tasks; these defaults are consumed by `tasks/main.yml` and the copied `build_linux.py` script.

State and persistence behavior: defaults place kernel source, object tree, and results under `{{ data_path }}/build`. Enabling storage causes the role to format and mount `build_linux_device`.

Dependencies and integration: `linux_git_url` defaults to `bootlinux_tree` or Torvalds' tree, tying the benchmark to bootlinux/kernel configuration. Results feed workflow reporting under `workflows/build-linux/results` and target-side `build-results`.

Risks: repeat count 100 can be long and storage-heavy. `shallow_clone=true` with depth 1 limits tag/history operations unless later fetching succeeds. An empty `build_linux_device` is dangerous if storage is enabled without inventory validation.

Test signals: inspect resolved vars before running; a smoke run with low repeat count should create source/build directories and a summary JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml -->
