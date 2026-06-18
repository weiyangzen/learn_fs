<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml

Source read: complete file, 16 lines, 496 bytes, sha256 `7a90edfef861cdba`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml_research.md`.

Purpose: defaults for optional QEMU source build/install support.

Important APIs/types/functions: variables include `qemu_build`, `qemu_force_install_if_present`, `qemu_bin_path`, `qemu_data`, `qemu_git`, `qemu_version`, `qemu_build_dir`, `qemu_target`, `build_linux_shallow_clone`, and `build_linux_clone_depth`.

Control flow: no tasks; values are consumed by `build_qemu/tasks/main.yml` and dependency dispatchers.

State and persistence behavior: when enabled, clone and build artifacts persist under `{{ data_path }}/qemu`, with install targeting `/usr/local/bin/qemu-system-x86_64` by default.

Dependencies and integration: supports kdevops workflows that require a custom QEMU, especially storage/CXL behavior not available in distro QEMU.

Risks: default version `v7.2.0-rc4` is old and pre-release. The `build_linux_*` variable names in this QEMU role may be confusing or unused here.

Test signals: with defaults no QEMU build should happen; enabling `qemu_build` should drive clone/configure/build/install unless a usable binary already exists and force is false.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml -->
