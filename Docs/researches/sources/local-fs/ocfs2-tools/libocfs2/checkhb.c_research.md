# File Research: sources/local-fs/ocfs2-tools/libocfs2/checkhb.c

Checks OCFS2 devices for heartbeat and mount state.

`ocfs2_check_heartbeats()` iterates an `ocfs2_devices` list, opens each device read-only with heartbeat-device allowance, marks OCFS2 fs type, detects heartbeat-device incompat feature, optionally checks local mount flags, copies label/UUID, determines stack/cluster naming, and for normal volumes loads the slot map to detect cluster-mounted state.

Errors opening non-OCFS2 devices are ignored so scanning can continue. Slot-map errors are stored per device and suppressed at the top level. Local mount checks can be skipped for heartbeat devices via `ignore_local`.

`ocfs2_get_ocfs1_label()` is a compatibility helper that reads the OCFS1 volume label sector at byte offset 512 and copies label and UUID fields.
