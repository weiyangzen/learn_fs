<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml

Source read: complete file, 9 lines, 304 bytes, sha256 `c3387be4d42d6362`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml_research.md`.

Purpose: defaults for the CXL/ndctl workflow role.

Important APIs/types/functions: `ndctl_git`, `ndctl_data`, `ndctl_version`, `ndctl_meson_testlog`, `kdevops_run_cxl_tests`, `kdevops_enable_cxl_dcd`, and `kdevops_qmp_str`.

Control flow: no direct tasks; consumed by CXL build/setup/test tasks.

State and persistence behavior: enabled role clones ndctl under `{{ data_path }}/ndctl`, builds it, may convert CXL/DAX memory to system RAM, and may collect Meson logs.

Dependencies and integration: integrates with QEMU CXL devices, QMP dynamic capacity commands, ndctl/daxctl/cxl utilities, kernel CXL modules, and kdevops result collection.

Risks: `ndctl_version` default `pending` must exist in the repository. Dynamic capacity and memory onlining are destructive/host-stateful operations.

Test signals: variable resolution should confirm whether classic CXL memory or DCD path is selected and whether test execution is enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml -->
