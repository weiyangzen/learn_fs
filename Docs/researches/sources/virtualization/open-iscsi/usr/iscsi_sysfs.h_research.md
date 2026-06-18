# File Research: sources/virtualization/open-iscsi/usr/iscsi_sysfs.h

## Purpose
`iscsi_sysfs.h` declares the public sysfs-facing API implemented by `iscsi_sysfs.c`. It is the main contract for querying iSCSI sessions, hosts, interfaces, transports, flashnodes, negotiated values, SCSI device state, and scan/rescan controls.

## Exports
- Constants: `SCSI_MAX_STATE_VALUE` and `ISCSID_RESP_POLL_TIMEOUT`.
- Callback typedefs for session, host, flashnode, and iface iteration.
- Session APIs: get session info by ID, iterate sessions, count sessions, test lead connection, parse sid from path, read session state, read negotiated/auth config, expected StatSN, NOP support, and user/kernel creator.
- Host/iface APIs: iterate hosts, find host by sid/hardware info/MAC, read host info, iterate ifaces on a host, read host state.
- Flashnode APIs: iterate/read/update/create/delete/login/logout flashnodes.
- SCSI device APIs: map LUN to blockdev, get device state, iterate devices, set queue depth, online/rescan devices, scan host.
- Transport APIs: get transport by HBA/session/sid/name, test loaded transport, free global transports.
- The global `transports` list.

## Integration Notes
The header includes `sysfs.h`, `types.h`, `iscsi_proto.h`, and `config.h`, forward-declares the main record structures, and provides `is_valid_operational_value()` as a small inline sentinel check for negotiated values where `-1` means invalid or unavailable.

## Risk Notes
The declarations expose kernel/sysfs implementation details directly to higher-level code. Callers need to preserve the conventions used by `iscsi_sysfs.c`, especially callback return semantics and error out-parameters.
