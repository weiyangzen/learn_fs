# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify22.c

Purpose: verifies `FAN_FS_ERROR` events from corrupted ext4 filesystems. It triggers filesystem aborts and bad inode/link lookups, then checks error records, error counts, and fid records.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark` with `FAN_MARK_FILESYSTEM`, `FAN_FS_ERROR`, `fanotify_event_info_error`, `fanotify_event_info_fid`, `get_event_info_error`, `get_event_info_fid`, `debugfs -w -R`, `fanotify_save_fid`, `poll`, and ext4-only LTP filesystem selection.

Control flow: `pre_corrupt_fs()` creates baseline directories, saves expected fids, unmounts the filesystem, corrupts inode mode and creates a bad link with `debugfs`, then remounts. Each test marks the filesystem for `FAN_FS_ERROR`, triggers one or more errors, polls and reads until enough error counts accumulate, consolidates multiple events, validates metadata, validates generic error info, validates fid identity, removes the mark, and remounts to reset error state.

State/persistence behavior: deliberately corrupts an ext4 test device and repeatedly unmounts/remounts to enter and recover from error states. `null_fid`, `bad_file_fid`, and `bad_link_fid` are persistent expected state within the process.

Dependencies/integration: requires root, ext4, `debugfs`, file-handle support, and specific kernel support tagged in the file. It is tightly coupled to LTP block-device mount orchestration.

Risks/test signals: destructive to the scratch test filesystem by design. Failures show as missing events, wrong errno, wrong aggregate count, missing fid/error records, or mismatched fsid/file handle.
