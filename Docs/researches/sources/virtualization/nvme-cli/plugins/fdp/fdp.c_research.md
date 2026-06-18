# File Research: sources/virtualization/nvme-cli/plugins/fdp/fdp.c

- Purpose: plugin for managing NVMe Flexible Data Placement devices.
- Log commands: `configs`, `usage`, `stats`, and `events` retrieve FDP configuration, reclaim-unit handle usage, FDP statistics, and FDP events through libnvme helper APIs.
- Variable-length handling: configuration, usage, and RUH status commands first fetch headers, compute required length, allocate buffers, then refetch full data.
- I/O command support: `status` and `update` use FDP reclaim unit handle status passthrough commands; `update` parses comma-separated placement IDs.
- Feature control: `set-events` updates `NVME_FEAT_FID_FDP_EVENTS`; `feature` shows, enables, or disables FDP configuration for an endurance group.
- Output: uses common FDP print wrappers and supports raw binary/human-readable flags where applicable.
- Validation: requires endurance-group IDs for several commands and validates placement/event list presence.
