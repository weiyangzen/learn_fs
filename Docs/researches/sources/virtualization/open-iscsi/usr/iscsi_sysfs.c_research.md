# File Research: sources/virtualization/open-iscsi/usr/iscsi_sysfs.c

## Purpose
`iscsi_sysfs.c` is the userspace facade over the Linux iSCSI, SCSI host, SCSI device, interface, transport, and flashnode sysfs trees. It translates kernel sysfs layout into open-iscsi records such as `session_info`, `host_info`, `iface_rec`, transport descriptors, negotiated session/connection configuration, flashnode records, and SCSI LUN state. It is used by `iscsiadm`, `iscsid`, login/logout code, firmware/offload paths, and session recovery.

## Main Responsibilities
- Maintains the global `transports` list by scanning `/sys/class/iscsi_transport`, reading transport `handle` and `caps`, applying transport templates, and optionally loading transport kernel modules.
- Reads session and connection attributes from `/sys/class/iscsi_session` and `/sys/class/iscsi_connection`, including target identity, CHAP credentials, timeout values, portal addresses, TPGT, negotiated digest/segment/session values, creator, state, and expected StatSN.
- Maps between session IDs, host numbers, target numbers, SCSI device IDs, block devices, and transport objects using sysfs lookup helpers and parent traversal.
- Reads host/interface information from `/sys/class/iscsi_host`, `/sys/class/scsi_host`, and host-local `iscsi_iface` directories, including MAC, netdev, IP settings, VLAN, DHCP, IPv6, TCP, digest, login, CHAP, and boot metadata.
- Reads and iterates hardware flashnode records under `/sys/bus/iscsi_flashnode/devices`, filling the nested session and connection fields of `flashnode_rec`.
- Iterates sessions, hosts, host ifaces, flashnodes, and SCSI devices with callback-based APIs declared in `iscsi_sysfs.h`.
- Writes operational sysfs controls such as SCSI `queue_depth`, device `state`, LUN `rescan`, and host `scan`.

## Important APIs and Control Flow
- `read_transports()` scans transport names, avoids duplicate list entries, reads `handle`/`caps`, applies the `qla4xxx` data-path-offload compatibility bit, and updates `num_transports`.
- `iscsi_sysfs_get_transport_by_name()` calls `read_transports()`, searches loaded transports, tries `transport_load_kmod()` once on miss, and retries the scan.
- `iscsi_sysfs_get_transport_by_hba()` reads the SCSI host `proc_name`, strips the `iscsi_` prefix for transport names such as `iscsi_tcp`, and resolves the transport list entry.
- `iscsi_sysfs_get_host_no_from_sid()` looks up `sessionN`, gets its sysfs device, then finds a SCSI parent or `host*` ancestor. This is a central bridge from iSCSI session IDs to SCSI host numbers.
- `iscsi_sysfs_read_iface()` is the largest reader: it combines host attributes, optional session attributes, optional kernel iface attributes, and optional boot info into an `iface_rec`. It handles older kernels that lack newer session or iface files by logging debug messages and falling back to defaults.
- `iscsi_sysfs_get_sessioninfo_by_id()` validates `sessionN`, reads target, CHAP, timeouts, TPGT, connection addresses/ports, host number, and iface data, with compatibility fallbacks for drivers that omit current or persistent portal attributes.
- `iscsi_sysfs_for_each_session()` scans sessions, fills a reusable `session_info`, and invokes a callback either in-process or through forked children. Non-parallel callbacks use `0` for match/success, negative for no-match, and positive for error; the parallel path converts child exit codes back to similar semantics.
- `iscsi_sysfs_for_each_device()` derives the target number from a session, scans SCSI LUN entries under the session's target path, parses `host:bus:target:lun`, and invokes a device callback.
- `iscsi_sysfs_scan_host()` can fork an async scanner; for rescans it onlines offline devices and rescans each LUN, otherwise it writes `- - -` to the SCSI host `scan` attribute.

## Dependencies and Integration
This file depends heavily on local sysfs wrappers from `sysfs.h`, open-iscsi record definitions from `iface.h`, `host.h`, `session_info.h`, `flashnode.h`, transport setup from `transport.h`, logging from `log.h`, IDBM/field constants, and error constants from `iscsi_err.h`. It exposes the sysfs layer consumed by administration, daemon recovery, firmware discovery, interface configuration, and host/flashnode management paths.

## Risk Notes
- The code intentionally supports many kernel-era sysfs layouts and driver quirks; fallback behavior is part of the API surface.
- Several helpers return `0` as both a legitimate host number and as an error sentinel paired with an out-parameter error code, so callers must check the error output.
- Some paths call `exit(1)` on invalid user-provided session paths, which makes the parsing helper unsuitable for library-style use without process termination.
- Parallel session iteration exits child processes with callback return values, so negative callback returns are truncated to `255` and explicitly interpreted as no-match.
- Sysfs races are expected: sessions and devices may disappear during scans, and many read failures are logged at debug level rather than fatal.
