<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml

Source read: complete file, 109 lines, 2729 bytes, sha256 `96af79fafd95290f`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml_research.md`.

Purpose: main orchestration for optional QEMU source clone, configure, build, and install.

Important APIs/types/functions: optional `include_vars`, `stat` for `qemu_bin_path`, `include_tasks: install-deps/main.yml`, `set_fact build_qemu_now`, `file`, `git`, `command` for Meson subproject/configure/nproc, `community.general.make`, and privileged install through `{{ make }} install`.

Control flow: load extra vars; verify local QEMU binary when building; install deps if building and force or binary absent; initialize and maybe set `build_qemu_now`; ensure `local_dev_path`; clone QEMU; delete old build dir; run `meson subprojects download` despite the task name "Disable downloads"; configure with `--disable-download`; build with `nproc.stdout`; install with sudo.

State and persistence behavior: creates `local_dev_path`, clones/updates `qemu_data`, removes `qemu_build_dir`, builds in the source tree, and installs QEMU into the system prefix. Facts control later tasks.

Dependencies and integration: depends on distro dependency tasks, `num_jobs`, `make`, `local_dev_path`, data path defaults, and the configured QEMU upstream tag. It feeds kdevops VM/workflow execution that needs the built QEMU binary.

Risks: `build_qemu_now` is set true only when `qemu_present.stat is not defined` rather than when the file is absent; after the stat task runs and the binary is missing, this condition may not build as intended. `GIT_SSL_NO_VERIFY=true` weakens clone verification. The "Disable downloads" task actually downloads subprojects before configure disables downloads.

Test signals: test both missing-binary and force-install paths. A missing `qemu_bin_path` with `qemu_build=true` should result in clone/configure/build/install; if not, the `build_qemu_now` condition is faulty.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml -->
