# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.c

Purpose: default JPEG library error, warning, trace, and message formatting implementation.

Key routines:
- Builds `jpeg_std_message_table[]` by reincluding `jerror.h` with `JMESSAGE` defined.
- `error_exit()` outputs the message, destroys the JPEG object, and exits with failure.
- `output_message()` formats and prints to stderr, or to a Windows message box if configured.
- `emit_message()` applies warning/trace policy.
- `format_message()` looks up the message template and formats string or integer parameters.
- `reset_error_mgr()` clears warning count and message code for a new image.
- `jpeg_std_error()` fills a `jpeg_error_mgr` with default methods and message tables.

Important behavior:
- Default fatal errors do not return; applications can override `error_exit` for `setjmp`/`longjmp` recovery.
- Only the first warning is printed unless trace level is at least 3, but all warnings are counted.
- Add-on message tables are supported.
- Uses `sprintf` into a buffer expected to be at least `JMSG_LENGTH_MAX`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jversion.h`, `jerror.h`, C stdio/stdlib behavior.

Notes:
- This is general IJG support used by both compression and decompression.
