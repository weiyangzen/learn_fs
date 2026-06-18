# File Research: sources/virtualization/open-iscsi/usr/iscsistart.c

## Purpose
`iscsistart.c` implements a small boot-oriented initiator program. It starts a private event-loop child using a PID-specific management socket namespace, logs into one configured target or firmware-provided boot targets, then asks the child event loop to stop. It is intended for root boot and early userspace scenarios.

## Startup and Login Flow
`main()` initializes a default `config_rec`, parses target, portal, TPGT, CHAP, initiator, firmware, network, print, and arbitrary `--param` options, initializes logging/sysfs, validates required static parameters unless firmware targets are present, then forks. The parent sets the namespace to the child PID, waits briefly for IPC, calls `setup_session()`, stops the event loop via `MGMT_IPC_IMMEDIATE_STOP`, waits for the child, and exits according to login/stop results. The child sets the same PID namespace, opens management IPC and kernel control device, fills daemon config, initializes the initiator, and runs `event_loop()`.

## Parameter Handling
- `parse_param()` parses `NAME=VALUE` into IDBM user parameters.
- `apply_params()` applies user parameters to a node record, clearing stale iface binding fields when users override netdev, MAC, or transport, and fills boot-friendly defaults: high initial login retry max, NOP disabled, and default scan mode.
- Static command-line CHAP values populate `config_rec.session.auth` directly with length checks.

## Firmware and Network Operations
`--fwparam_connect` reads firmware boot entry/targets and logs into firmware targets. `--fwparam_network` exits after applying firmware NIC setup. `--fwparam_print` prints firmware target entries and exits.

## Integration Notes
This file reuses daemon infrastructure (`event_loop`, `mgmt_ipc`, `iscsi_ipc`, `initiator`, `iscsid_req`) without running the full persistent `iscsid`. It defines its own `dconfig` and stubs `session_in_use()` to return `0`.

## Risk Notes
- The parent uses a short `sleep(1)` after forking before sending login requests; slow startup depends on retry behavior in `login_session()`.
- Static parameter parsing mutates the `--param` string in place.
- `session_in_use()` is a stub in this binary, so safe-logout mount-use checks are not available here.
