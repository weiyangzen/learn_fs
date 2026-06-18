# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.c

Implements `workload-tracker`, a live workload tracking capture command.

NVMe IDs:
- Log page `0xf9`.
- Feature `0xf1`.
- Trigger threshold feature `0xf5`.

Data model:
- `WorkloadLogEnable` bitfield config controls tracker enable, trigger enable, sample time, content group, stop count, and event dump.
- `workloadLog` holds version, counts, timestamps, config, trigger values, and up to 126 32-byte entries.
- Field definitions describe seven content groups: Base, CmdQ, Pattern, RandSeq, Throttle, Power, Defrag.

Main behavior:
- Parses options for UUID index, enable/disable, sample time, type, run time, flush frequency, wall clock, trigger field, threshold, delta, and latency-trigger mode.
- Validates sample interval and tracker type against string tables.
- Computes trigger bitfield location from selected field offset and size.
- Optionally enables tracker.
- Polls log page, printing only entries newer than the last timestamp.
- Optionally reconstructs wall-clock timestamps from SSD timestamp deltas.
- Optionally disables tracker and trigger at the end.

Output:
- Header/field names are printed depending on verbosity and poll state.
- Entry fields are decoded by configured field sizes.

Risks/notes:
- Entry field loads cast unaligned bytes to `__u16`/`__u32`.
- Static `last_timestamp_us` persists across calls within process.
- Several log values are printed without endian conversion inside entry decoding.
