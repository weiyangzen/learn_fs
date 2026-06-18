<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml

Purpose: sets reboot-loop count, test type, data paths, systemd-analyze logging, crash injection, and regular-vs-kexec comparison defaults.

Important APIs/types/functions: variables/facts `reboot_limit_test_type`, `reboot_limits_data`, `reboot_limits_systemctl_analyze_log`, `reboot_limits_count_log`, `reboot_limit_enable_systemd_analyze`, `reboot_limit_boot_count_crash_enable`, `reboot_limit_boot_crash_count`.

Control flow: Defaults feed main loop and per-reboot task files.

State and persistence behavior: No direct state; values determine reboot count and result paths.

Dependencies and integration points: Used by demos/reboot-limit workflow.

Risks: Aggressive defaults can repeatedly reboot or crash hosts; path changes affect result collection.

Test signals: Signals are expected variable values and correct mode selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml -->
