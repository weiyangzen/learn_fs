# sources/test-tools/kdevops/workflows/demos/reboot-limit/Kconfig

## Purpose
Defines the reboot-limit demo workflow for repeated reboot reliability testing and optional regular reboot vs kexec comparison.

## Important APIs, Types, and Functions
Important symbols include `WORKFLOWS_REBOOT_LIMIT`, `KDEVOPS_WORKFLOW_NAME`, reboot type choices, `REBOOT_LIMIT_TEST_TYPE`, `REBOOT_LIMIT_COMPARE_BOTH_ENABLED`, `REBOOT_LIMIT_BOOT_MAX`, watchdog symbols, loop steady-state symbols, crash-injection symbols, data paths, and `REBOOT_LIMIT_ENABLE_SYSTEMD_ANALYZE`.

## Control Flow
When enabled, users choose reboot mechanism, optional loop behavior, optional crash injection, and optional data collection. Compare mode creates separate regular and kexec data paths.

## State and Persistence Behavior
Configuration persists in `.config` and YAML. Runtime data persists under configured reboot-limit directories on targets and in copied results.

## Dependencies and Integration Points
Consumed by the reboot-limit Makefile and `playbooks/reboot-limit.yml`. Depends on Ansible reboot, systemd reboot/kexec support, and optional systemd-analyze.

## Risks and Edge Cases
Large reboot counts multiplied by loop goals can create very long runs. Compare mode doubles state paths. Crash injection is disruptive and should be isolated.

## Test Signals
Exercise each reboot type, compare mode, `COUNT` override, loop resume behavior, data collection on/off, and crash injection in disposable VMs.
