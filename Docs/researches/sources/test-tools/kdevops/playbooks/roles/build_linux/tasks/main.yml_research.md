<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml

Source read: complete file, 245 lines, 8141 bytes, sha256 `333bea63daf7cd58`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml_research.md`.

Purpose: full orchestration for repeated Linux kernel build benchmarking, including optional filesystem setup, source checkout validation, script deployment, asynchronous builds, and result summary display.

Important APIs/types/functions: `set_fact`, `stat`, `shell`, `command`, `ansible.builtin.filesystem`, `ansible.posix.mount`, `ansible.builtin.git`, `copy`, `slurp`, `from_json`, and `debug`. It calls `build_linux.py` with source/build/results/count/jobs/target/clean/stats/tag arguments.

Control flow: install deps; infer filesystem type and optional XFS block size from hostname for multifs testing; optionally format and mount a dedicated build filesystem; create source/build/result dirs; validate existing git repo; delete corrupt repo; shallow or full clone Linux; optionally fetch tags; ensure data dir ownership; copy the Python benchmark script; run repeated kernel builds asynchronously with a 10-hour timeout; display stdout; read summary JSON and print aggregate statistics.

State and persistence behavior: can destructively reformat `build_linux_device`, mounts `{{ data_path }}/build`, creates/chowns directories, clones or removes a Linux source tree, writes `{{ data_path }}/build_linux.py`, and produces summary JSON under `{{ data_path }}/build-results`.

Dependencies and integration: integrates with workflow flags, `bootlinux_tree`, `build_linux_*` vars, the external `workflows/build-linux/scripts/build_linux.py`, git, mkfs tools, `mkfs.xfs`, Ansible mount/filesystem modules, and target hostname conventions for multifs.

Risks: enabling storage with the wrong device can wipe data. The `mount_check` shell greps broad mount output. If an existing `.git` directory is corrupt, the source directory is removed. Long async builds can hide early failures until polling completes. Tag fetching is skipped when the source dir is not writable.

Test signals: smoke with `build_linux_repeat_count=1`; verify filesystem type/mount when storage is enabled; confirm clone path, build script copy, nonzero stdout, and `summary_{{ ansible_hostname }}.json` with total/success/failure/time fields.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml -->
