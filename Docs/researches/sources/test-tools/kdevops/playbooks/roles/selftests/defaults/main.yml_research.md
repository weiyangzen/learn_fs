<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml

Purpose: defines Linux selftests source/build/run defaults, data paths, section toggles, timeout controls, and special target behavior.

Important APIs/types/functions: variables/facts `data_path`, `target_linux_tree`, `target_linux_dir_path`, `bootlinux_9p_host_path`, `kdevops_workflow_enable_selftests`, `kdevops_run_selftests`, `run_tests_on_failures`, `selftests_skip_run`, `selftests_skip_reboot`, `selftests_build_radix_tree`.

Control flow: Defaults guide dependency install, make targets, userspace/kernelspace splitting, and result collection in `selftests/tasks/main.yml`.

State and persistence behavior: No direct state; values determine what is built and run.

Dependencies and integration points: Consumed by the selftests workflow and 9p build path support.

Risks: Incorrect target toggles can build or run the wrong selftest subset. Timeout defaults affect false failures on slow hosts.

Test signals: Signals are expected target variables and matching make/run commands.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml -->
