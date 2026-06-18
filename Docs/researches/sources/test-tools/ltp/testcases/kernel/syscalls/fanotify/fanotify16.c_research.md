# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify16.c

Purpose: validates fanotify directory-entry modification reporting across `FAN_REPORT_DFID_NAME`, `FAN_REPORT_DIR_FID`, `FAN_REPORT_DFID_FID`, `FAN_REPORT_DFID_NAME_FID`, and `FAN_REPORT_DFID_NAME_TARGET`. It covers create, delete, move, rename, open, close, self events, child events, and ignored rename masks on filesystem and inode marks.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `fanotify_event_metadata`, `fanotify_event_info_fid`, `file_handle`, `fanotify_save_fid`, `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, `SAFE_MOUNT`, `SAFE_UMOUNT`, and `name_to_handle_at` availability via `HAVE_NAME_TO_HANDLE_AT`. Local `event_t` captures expected masks, parent fid, child fid, names, and old/new rename names.

Control flow: `setup()` probes required fanotify capabilities, prepares mount-relative paths, and creates a temp directory. `do_test()` selects a case, initializes a group, marks either the mounted filesystem or watched directories, creates and bind-mounts a subdirectory, records expected fids, generates file and directory operations, reads the event buffer, then walks events while checking mask merging, info record type, fid bytes, fsid, filename, pid, and optional child fid records.

State/persistence behavior: the test mutates a mounted scratch filesystem, creates and removes files/directories, bind-mounts a subdirectory, and relies on fanotify queue state accumulated between operations and reads. Expected state is held in `event_set`; the actual persistent filesystem state is cleaned by unlink, rmdir, unmount, and closing the notification fd.

Dependencies/integration: integrates the LTP fanotify compatibility header, filesystem test matrix, root-only mounting, file-handle support, and kernel feature probes for filesystem marks, target fid reporting, and `FAN_RENAME`.

Risks/test signals: high sensitivity to filesystem event ordering and kernel merge rules. Failures are precise `TFAIL` diagnostics for extra/missing events, wrong info type, wrong handle, wrong name, wrong pid, or unexpected child-fid cardinality; unsupported kernel features are reported as `TCONF`.
