# File Research: sources/virtualization/nvme-cli/libnvme/test/config/hostnqn-order.c

## Purpose
Tests precedence order for host NQN and host ID selection.

## Test Cases
- `command_line()` passes explicit hostnqn/hostid arguments and verifies they override other sources.
- `json_config()` clears environment values, reads JSON before scanning, and verifies the first JSON host is selected by default.
- `from_file()` sets `LIBNVME_HOSTNQN` and `LIBNVME_HOSTID` environment values and verifies they are selected when no command-line args are given.

## Relevance
Validates the documented host identity resolution order used by Linux NVMe and libnvme config flows.
