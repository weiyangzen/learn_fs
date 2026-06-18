# File Research: sources/local-fs/xfsdump/common/content_common.c

Purpose: shared content-layer helper for prompting the operator to change media.

Key behavior:
- Implements `Media_prompt_change(drive_t *drivep)`.
- Builds a dialog with preamble, question, choices, acknowledgment, and postamble using the dlog API.
- Prompts for media change on the given drive index with two choices:
  - media change declined
  - media changed
- Uses a one-hour timeout (`DLOG_TIMEOUT = 3600`), defaulting to “media changed”; timeout and hangup/quit paths map to decline except SIGINT.
- On SIGINT, if child stop was not requested, waits briefly to let the main thread handle its dialog, logs a bare message to synchronize with logging locks, then retries.

Interactions:
- Depends on `dlog_begin`, `dlog_multi_query`, `dlog_multi_ack`, and `dlog_end`.
- Checks `cldmgr_stop_requested` to abort cleanly if the main control path requested worker termination.
- Uses `fold_init` and `mlog` for dialog formatting/synchronization.

Risks/notes:
- Uses fixed-size `question[100]`; current formatted string is small.
- Uses `goto retry` to re-enter the dialog after interrupts.
- Assumes `dlog_allowed` context has already been established by the caller before prompting.
