# File Research: sources/local-fs/dlm/dlm_controld/dlm_controld.h

## Purpose
Defines the private control-socket protocol between `dlm_controld` and `libdlmcontrol`.

## Main Contents
- Socket path names: `dlmc_sock` and `dlmc_query_sock`.
- Magic/version constants: `DLMC_MAGIC` and `DLMC_VERSION`.
- Command IDs for debug dumps, plock dumps, lockspace/node queries, fs registration notifications, deadlock checks, fence ack, status/config dumps, run operations, config reload, and online config setting.
- `struct dlmc_header` with magic, version, command, option, payload length, small embedded data field, flags, and a fixed lockspace name buffer.
- State transfer constants and `struct dlmc_state` for daemon, daemon-node, startup-node, and run state messages.
- `struct dlmc_run_check_state` for run-check status.

## Integration Points
- Included by `dlm_daemon.h` and `libdlmcontrol.h` users.
- State constants are produced by `daemon_cpg.c` and consumed by control clients.

## Risks and Notes
- Field `unsued2` is misspelled but part of the local ABI layout.
- Lockspace names have no terminating null space in `dlmc_header.name`, so consumers must treat them as fixed-length fields.
- Header changes affect daemon/control-library compatibility.
