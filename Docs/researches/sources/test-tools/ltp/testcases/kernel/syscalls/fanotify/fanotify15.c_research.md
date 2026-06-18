# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify15.c

Purpose: Verifies `FAN_REPORT_FID` dirent events with create/delete/move/modify/delete-self merging for filesystem and parent-directory marks.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_CREATE`, `FAN_DELETE`, `FAN_MOVE`, `FAN_MODIFY`, `FAN_DELETE_SELF`, `FAN_ONDIR`, `FAN_EVENT_ON_CHILD`, `fanotify_save_fid`, and event fid comparison.

Control flow: Each case marks `TEST_DIR`, saves fids for the root/file/subdir, creates/modifies/renames/unlinks a file, reads file events, then creates/renames/removes a directory and reads directory events. It verifies merged masks and fid/fsid/handle identity.

State and persistence behavior: State is the mounted test directory tree, file and directory fids, fanotify mark, and event buffer. Events are expected to merge by object.

Dependencies and integration points: Requires root, mounted all-filesystems coverage, `name_to_handle_at`, and fid support; filesystem marks are feature-gated.

Risks and test signals: The test is sensitive to event merge order and handle stability. It is tagged for the duplicate parent/child merge regression.
