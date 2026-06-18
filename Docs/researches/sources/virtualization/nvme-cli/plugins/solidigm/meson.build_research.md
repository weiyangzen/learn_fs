# File Research: sources/virtualization/nvme-cli/plugins/solidigm/meson.build

Meson build fragment for the Solidigm plugin. It adds Solidigm plugin sources to `plugin_sources`, including command registration, utility, SMART, garbage collection, latency, log-page directory, telemetry, internal logs, market log, temperature stats, drive info, OCP version, and workload tracker modules.

It also descends into `solidigm-telemetry` with `subdir('solidigm-telemetry')`.

Files from this work item included here:
- `solidigm-garbage-collection.c`
- `solidigm-get-drive-info.c`
- `solidigm-id-ctrl.c`
- `solidigm-internal-logs.c`
