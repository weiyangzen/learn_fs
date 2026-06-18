# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jerror.c

Default IJG error, warning, trace, and message-formatting manager.

Key points:
- Builds `jpeg_std_message_table` by re-including `jerror.h` with `JMESSAGE` mapped to string entries.
- Default `error_exit` outputs the current message, destroys the JPEG object to clean temporary resources, and exits with failure.
- `output_message` formats the current message and writes it to stderr, or optionally to a Windows message box.
- `emit_message` prints the first warning by default, counts all warnings, and emits trace messages according to `trace_level`.
- `format_message` looks up standard or add-on message text, falls back on the generic bad-message string, and formats integer or string parameters.
- `reset_error_mgr` clears warning count and message code while preserving application method overrides and trace level.
- `jpeg_std_error` initializes all method pointers, message tables, trace/warning state, and add-on table bounds.

Dependencies and interactions:
- Used by both compressor and decompressor objects unless applications install custom handlers.
- Error macros throughout the library populate `err->msg_code` and `msg_parm` before calling these methods.

Risk notes:
- Default fatal handling exits the process; embedding applications usually need to override `error_exit` with `setjmp`/`longjmp` or equivalent recovery.
- Formatting uses `sprintf` into `JMSG_LENGTH_MAX`; message definitions must remain bounded.
- Warning policy suppresses repeated corrupt-data warnings unless high tracing is enabled.
