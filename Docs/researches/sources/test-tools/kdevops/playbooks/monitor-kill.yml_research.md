# sources/test-tools/kdevops/playbooks/monitor-kill.yml

Purpose: kills monitoring processes and removes monitoring data on target hosts and local collected result directories.

Important APIs/types/functions: first play targets `baseline:dev` with sudo, optional `include_vars`, `pgrep`, `pkill`, PID-file deletion, `stat`, `find`, data directory removal, and process verification. Second play targets localhost and removes `{{ topdir_path }}/workflows/build-linux/results/monitoring` when cleanup is enabled.

Control flow: load optional variables, find and kill fragmentation and folio migration monitors, remove PID files, optionally delete `/root/monitoring`, verify no matching processes remain, then clean local monitoring results.

State/persistence behavior: mutates running process state and deletes remote/local monitoring artifacts when `enable_monitoring_cleanup` defaults true.

Dependencies/integration: cleanup companion for monitoring tasks imported by build-linux, MinIO, AI, and other workflows.

Risks/test signals: `pkill -f` patterns may match unintended processes; default cleanup deletes collected data. Test signals are no remaining monitor processes, absent PID files, and expected directory removal only when cleanup is enabled.
