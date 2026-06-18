<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml

Purpose: builds, runs, collects, and validates Linux kernel selftests for the selected kdevops selftests workflow.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`, `ansible.builtin.import_tasks`, `ansible.builtin.set_fact`, `ansible.builtin.debug`, `ansible.builtin.fail`, `ansible.builtin.file`, `ansible.builtin.command`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `is_selftest_xarray`, `is_selftest_maple`, `is_selftest_vma`, `selftest_xarray`, `selftest_maple`, `selftest_vma`, `selftest_userspace`; tasks `Import optional extra_args file`, `Install dependencies`, `Install dependencies to build Linux selftests on host`, `Check if this node is in charge of running kernel or userspace tests`, `Check if this node is in charge of userspace tests`.

Control flow: Loads extra vars and deps, classifies hosts into userspace special tests versus kernelspace, prepares firmware/configfs/data, computes make targets, builds selftests on target or localhost 9p, installs built tests, runs special radix-tree/userspace/kernelspace commands, gathers dmesg/TAP/log files, fetches results by kernel, and fails if TAP logs contain `not ok`.

State and persistence behavior: Persists built selftests under data paths, installed selftest workdir, local result trees under `workflows/selftests/results`, watchdog marker files, dmesg/tap/userspace/module logs, and failure facts.

Dependencies and integration points: Depends on kernel source tree paths, make, distro deps, 9p sharing when enabled, host naming conventions for xarray/maple/vma, and workflow variables.

Risks: There is a duplicate `Build selftests` task. Host-name-derived target selection is brittle. TAP failure scan is simple substring matching and may overmatch comments. Cleaning last-run can remove concurrent data.

Test signals: Signals are build/install success, created logs per host, fetched results under last kernel, absence/presence of TAP `not ok`, and correct userspace/kernelspace routing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml -->
