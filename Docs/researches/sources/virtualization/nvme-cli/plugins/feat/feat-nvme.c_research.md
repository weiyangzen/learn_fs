# File Research: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.c

- Purpose: named command wrappers for getting and setting selected NVMe feature IDs.
- Generic get path: `feat_get_nsid()` optionally obtains feature data length, allocates a buffer, calls `nvme_get_features`, and prints decoded feature output.
- Supported features: power management, performance characteristics, host controlled thermal management, timestamp, temperature threshold, arbitration, volatile write cache, power limit, power threshold, power measurement, error recovery, number of queues, and host behavior support.
- Set behavior: constructs correct CDW fields with NVME_SET macros and calls either generic `nvme_set_features` or specialized init helpers for temperature/arbitration/host behavior.
- Partial updates: temperature threshold, arbitration, number of queues, and host behavior read current or saved values first so unspecified fields can be preserved.
- Data payloads: timestamp and host behavior use structured payloads; performance characteristics can read vendor-specific attribute data from a file.
- CLI integration: the `FEAT_ARGS` macro adds common `--save` and `--sel` options to each feature command.
- Notable issue: `num_queues_set()` appears to OR an unspecified `ncqr` value into `FEAT_NRQS_NSQR` rather than `FEAT_NRQS_NCQR`, likely a typo in preserving existing completion queue count.
