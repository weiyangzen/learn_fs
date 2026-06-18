# sources/user-network-fs/s3fs-fuse/src/s3fs_help.h

Purpose: declares the small public help/version surface used by CLI parsing and startup logging.

Important APIs: `show_usage()`, `show_help()`, `show_version()`, and `short_version()`.

Control flow: command-line parsing calls the printing functions for help/version/error paths; `print_launch_message` uses `short_version()` for startup logs.

State and persistence: no state is declared. The implementation reads shared globals and compile-time macros.

Dependencies and integration points: included by credential validation for usage output and by utility/startup code for launch messaging.

Risks: low implementation risk, but declarations are part of a broad CLI path; signature changes would ripple through startup and validation code.

Test signals: compile checks for all include sites and CLI smoke tests for help/version output.
