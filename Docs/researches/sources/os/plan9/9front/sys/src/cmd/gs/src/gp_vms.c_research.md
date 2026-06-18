# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_vms.c

Purpose: VAX/VMS platform implementation for Ghostscript.

Platform services: Provides no-op init/exit, VMS-convention exit mapping in `gp_do_exit`, VMS time conversion from quadword system time to seconds/nanoseconds since January 1, 1980, and `DECW$DISPLAY` lookup. Persistent cache routines are unimplemented stubs.

File and printer behavior: Defines VMS filename constants, list separator `,`, null device `NLA0:`, current directory `[]`, and binary modes. `gp_open_printer` uses VMS-specific `fopen` record options for binary pass-through or text records. `gp_open_scratch_file` combines temp directory and prefix, appends `XXXXXX`, calls `mktemp`, and opens the file.

File enumeration: Wraps VMS `LIB$FIND_FILE` with descriptor-based `file_enum`. Initialization translates Ghostscript `?` wildcards to VMS `%`, strips backslash quoting, and appends `.*` for trailing `*` without an extension. `gp_enumerate_files_next` returns VMS names from `LIB$FIND_FILE` until RMS no-more-files/error, then frees enumeration state.

Path combination: Implements VMS-specific roots and separators for device/logical names, `[`/`]` directories, `.` directory separators, and `-` parent references. `gp_file_name_combine` handles roots, device-relative concatenation, bracket unclosing, and then delegates to `gp_file_name_combine_generic`.

Dependencies and notes: Depends on VMS system calls/descriptors and Ghostscript generic path helpers. Parent traversal is reported as not allowed, and empty path items are meaningful.
