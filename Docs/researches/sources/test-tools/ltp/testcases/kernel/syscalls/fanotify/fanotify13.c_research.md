# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify13.c

Purpose: Verifies `FAN_REPORT_FID` events report correct file handles and fsids for open/close/delete-self events across base and overlay variants.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_NONBLOCK`, `FAN_OPEN`, `FAN_CLOSE_NOWRITE`, `FAN_DELETE_SELF`, `FAN_ONDIR`, `name_to_handle_at`, overlay helpers, bind mounts, and fid comparison.

Control flow: Setup creates file/directory objects, optional overlay mounts, an extra non-fid mark, and records each object's fid. Each variant/case marks objects, generates opens/closes or deletes, reads events, and compares mask, `FAN_NOFD`, handle bytes/type/content, and fsid.

State and persistence behavior: State includes base or overlay mount topology, object identities, saved fids, and fanotify event queues. Delete-self cases recreate objects afterward.

Dependencies and integration points: Requires root, mounted filesystems, `name_to_handle_at`, support for `AT_HANDLE_FID` on overlay variants, and feature gating for filesystem marks.

Risks and test signals: Overlay combinations are version-sensitive and tagged for kernel fixes. Wrong fid/fsid or unexpected fd in fid mode fails.
