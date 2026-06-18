<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Makefile -->
# sources/test-tools/kdevops/workflows/sysbench/Makefile

## Purpose
This Makefile defines sysbench setup, execution, telemetry, result collection, cleanup, plotting, monitoring, and help targets for kdevops.

## Important Targets and Variables
`TAGS_SYSBENCH_RUN` aggregates db start, connection test, post entrypoint, population, run, telemetry, logs, results, and plot tags. `TAGS_SYSBENCH_TEST`, `TAGS_SYSBENCH_TELEMETRY`, and `TAGS_SYSBENCH_RESULTS` prepend `vars` as needed. Targets include `sysbench`, `sysbench-test`, `sysbench-telemetry`, `sysbench-results`, `monitor-results`, `sysbench-clean`, `sysbench-plot`, and `sysbench-help-menu`.

## Control Flow
`sysbench` runs `playbooks/sysbench.yml` while skipping the run tag set, so it performs setup. `sysbench-test` runs the full tagged workload. Telemetry and results targets run narrower tag groups. Cleanup runs `vars,clean`; plotting runs `vars,plot`. `monitor-results` invokes `playbooks/monitor-results.yml` with `extra_vars.yaml` and, in the second definition, `LIMIT_HOSTS`.

## State, Persistence, and Dependencies
State is managed by Ansible: database containers or native services, populated tables, telemetry, logs, results, and plots. The Makefile depends on kdevops variables such as `space`, `comma`, `Q`, and `LIMIT_HOSTS`.

## Risks and Test Signals
`monitor-results` is defined twice, which can lead to make override warnings or the latter recipe replacing the former. Tag composition is central; missing tags silently skip phases. Test signals include playbook tag execution, result files, telemetry collection, and generated plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Makefile -->
