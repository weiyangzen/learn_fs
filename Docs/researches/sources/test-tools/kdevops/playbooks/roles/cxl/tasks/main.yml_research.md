<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml

Source read: complete file, 218 lines, 6279 bytes, sha256 `be88170abfbb06b7`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml_research.md`.

Purpose: full CXL workflow orchestration: build/install ndctl, configure CXL memory or dynamic capacity, optionally run CXL tests, and collect Meson test logs.

Important APIs/types/functions: optional `include_vars`, dependency include, `create_data_partition`, `git`, Meson setup/configure/compile/install commands, includes for `cxl-mem-setup`, `cxl-create-dc-region`, and `cxl-dcd-setup`, `uname -r`, `set_fact` result paths, `modprobe configfs/cxl_test`, `sysctl kernel.printk`, `meson test -C build --suite cxl`, `find`, and `fetch`.

Control flow: load vars, install deps, ensure data partition, clone ndctl, configure/build/install with destructive tests enabled, choose classic CXL memory or DCD setup, compute result paths and kernel version, remove prior local result directory, write last-kernel marker, optionally load modules and run CXL Meson tests, find test logs on targets, and fetch them to local workflow results.

State and persistence behavior: updates ndctl checkout/build tree, installs ndctl/cxl/daxctl tools, mutates CXL/DAX/system RAM state, changes kernel printk, loads/unloads modules, removes local result directories, and fetches logs.

Dependencies and integration: depends on QEMU CXL topology, CXL kernel config/modules, ndctl Meson project, data partition role, localhost result tree, and workflow tags for prep/run/copy phases.

Risks: ndctl build always runs, regardless of `kdevops_run_cxl_tests`. CXL setup tasks hard-code device names and are not idempotent. `last_kernel` is derived from `stdout_lines` with regex string cleanup, which is brittle. Test task uses `ignore_errors` and `no_log`, so failures can be easy to miss except via fetched logs.

Test signals: verify installed `cxl/ndctl/daxctl`, successful memory setup (`lsmem`), optional `cxl_test` module load/unload, presence of `testlog.txt`, and fetched results under `workflows/cxl/results/last-run/{{ last_kernel }}`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml -->
