# File Research: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.c

- Purpose: Amazon vendor plugin for EC2 NVMe identify-controller data and latency/statistics log page output.
- Identify support: decodes vendor-specific controller field `bdev` and prints it or adds it to JSON.
- Stats log: reads Amazon log page `0xD0`, recognizes EBS and local-storage magic values, and decodes totals for read/write ops, bytes, time, performance-exceeded counters, queue length, and latency histograms.
- Local storage behavior: detects Amazon EC2 NVMe Instance Storage by model prefix and may use namespace-specific log retrieval.
- Detail mode: for version 1 logs, can print per-I/O-size read/write histogram counts.
- JSON support: emits total counters and histogram arrays when `CONFIG_JSONC` is available.
- Polling mode: optional interval mode repeatedly fetches the log, computes deltas from previous cumulative counters/histograms, and stops on SIGINT.
- Notable issue: `get_stats()` validates a local `cfg.output_format` initialized to `"normal"` and does not expose it in command options, so global output-format handling appears inconsistent with other commands.
