# sources/test-tools/kdevops/kconfigs/monitors/Kconfig

Purpose: Kconfig fragment for optional monitoring services that run during workflows and collect system behavior data for performance analysis and debugging.

Important APIs/types/functions: top-level `ENABLE_MONITORING` gates all settings. Under `MONITOR_DEVELOPMENTAL_STATS`, it defines `MONITOR_FOLIO_MIGRATION`, `MONITOR_FOLIO_MIGRATION_INTERVAL`, `MONITOR_MEMORY_FRAGMENTATION`, `MONITOR_FRAGMENTATION_DURATION`, and `MONITOR_FRAGMENTATION_OUTPUT_DIR`, all emitted to YAML where appropriate.

Control flow: enabling monitoring exposes developmental stats; enabling each specific monitor controls role tasks that start/collect folio migration or eBPF fragmentation data. Interval and duration values parameterize collection cadence and lifetime.

State/persistence behavior: generated YAML controls background processes and data paths. Fragmentation output defaults to `/root/monitoring/fragmentation`; duration `0` means continuous until workflow completion.

Dependencies/integration: integrates with workflow playbooks that explicitly import `roles/monitoring/tasks/monitor_run.yml` and `monitor_collect.yml`, such as build-linux, MinIO, and AI benchmark playbooks. Runtime dependencies include root privileges, debugfs migration stats, python3-bpfcc, tracepoints, and matplotlib.

Risks/test signals: the help text still lists only fstests as currently supported while other playbooks import monitoring tasks. Developmental stats depend on non-upstream kernel patches. Test signals are correct YAML generation, monitor startup/cleanup, expected files under `/root/monitoring`, and no orphaned monitor processes after `monitor-kill.yml`.
