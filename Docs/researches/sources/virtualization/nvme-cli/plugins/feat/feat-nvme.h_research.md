# File Research: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.h

- Purpose: command-registration and shared macro header for the feature plugin.
- Descriptions: defines per-command description strings and `FEAT_PLUGIN_VERSION`.
- Macro: `FEAT_ARGS` wraps `NVME_ARGS` and adds common `save` and `sel` options.
- Plugin: `feat`, description `NVMe feature extensions`, version `1.0`.
- Commands: registers wrappers for power management, performance characteristics, HCTM, timestamp, temp threshold, arbitration, volatile write cache, power limit, power threshold, power measurement, error recovery, number of queues, and host behavior support.
