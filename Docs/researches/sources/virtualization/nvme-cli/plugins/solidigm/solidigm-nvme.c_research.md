# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.c

Defines wrapper functions for the Solidigm plugin command table.

Main behavior:
- Includes `solidigm-nvme.h` under `CREATE_CMD`, causing the command table macros to bind to functions in this file.
- Wraps local Solidigm implementations such as identify controller, SMART, internal logs, garbage collection, latency tracking, telemetry parsing, log page directory, market log, temp stats, drive info, OCP version, and workload tracker.
- Redirects some commands to OCP plugin implementations:
  - `vs-smart-add-log`
  - `clear-pcie-correctable-errors`
  - `clear-fw-activate-history`
  - `vs-fw-activate-history`

This file contains dispatch glue only; implementation logic lives in the included command modules.
