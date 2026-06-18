# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_smbtorture.c

Purpose: implements Samba-specific smbtorture FSCTLs gated by `smbd:FSCTL_SMBTORTURE` for testing timeout, response padding, read padding, and async close behavior.

Important APIs and types: `smb2_ioctl_smbtorture()` dispatches controls. `struct async_sleep_state` stores server connection and target fsp for delayed validity testing. `smbd_fsctl_torture_async_sleep_send()` creates a timed request; `smbd_fsctl_torture_async_sleep_done()` checks whether the fsp still exists with `files_forall()`.

Control flow: disabled configuration maps to device-appropriate unsupported status. `FORCE_UNACKED_TIMEOUT` requires empty input and sets `xconn->ack.force_unacked_timeout`. `IOCTL_RESPONSE_BODY_PADDING8` optionally fills output with byte 8 and sets `body_padding = 8`. `GLOBAL_READ_RESPONSE_BODY_PADDING8` sets connection-global read padding. `FSP_ASYNC_SLEEP` requires one input byte and a valid fsp, waits, then returns OK only if the original fsp remains in the open-file list, otherwise `FILE_CLOSED`.

State and persistence: connection fields for forced ack timeout and read padding persist for the live connection. Async sleep stores a raw fsp pointer for identity comparison only.

Dependencies and integration: depends on loadparm private parameter lookup, shared IOCTL state, tevent endtime, `files_forall()`, connection ack/read-padding fields, and common IOCTL response formatting.

Risks: these controls must stay disabled by default. The async fsp pointer must not be dereferenced after close. Time unit comments are confusing relative to `timeval_current_ofs(0, msecs)`. Padding controls must not affect production clients unless explicitly enabled.

Test signals: verify disabled behavior, input-length validation, response body padding layout, global read padding on later reads, forced unacked timeout, and async sleep behavior when close races the request.
