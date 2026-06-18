# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile.c

## Purpose
Implements non-I/O PostScript file operators, file-name parsing, library-path file opening, safe-mode permission checks, temp-file handling, and low-level file stream allocation/closing.

## Key Functions
- `zfile_init()` initializes the invalid closed-file stream.
- `check_file_permissions_reduced()` and `check_file_permissions()` enforce `PermitFileReading`, `PermitFileWriting`, and `PermitFileControl`.
- `zfile()` opens files or IODevices, including special `%statementedit%` and `%lineedit%` callout handling.
- `zdeletefile()`, `zrenamefile()`, and `zstatus()` implement Level 2 file-control/status operators.
- `zfilenameforall()` plus `file_continue()` and `file_cleanup()` enumerate matching files via IODevice callbacks.
- `zexecfile()` executes a file and guarantees close through e-stack cleanup.
- `zlibfile()` searches the Ghostscript library path and returns either a file or `false`.
- `ztempfile()` creates scratch files with restricted prefix/absolute-path checks.
- `parse_file_name()`, `parse_real_file_name()`, and `parse_file_access_string()` validate file operands.
- `zopen_file()`, `iodev_os_open_file()`, `file_open_stream()`, and `lib_file_open()` open streams over OS files and IODevices.
- `make_stream_file()` constructs `t_file` refs and sets read/write ids.
- `file_alloc_stream()` reuses closed stream objects at the same save level.
- `file_close_disable()`, `file_close_file()`, and `file_close()` implement close semantics and invalidate stale file refs.

## Important Behavior
- Stream objects carry serial ids; closing increments ids so stale PostScript file objects cannot access reused streams.
- Safe mode blocks `%pipe%` in `parse_file_name()` and applies permit-list matching after path reduction.
- Temp files created by `.tempfile` are allowed selected control operations through the `SAFETY/tempfiles` dictionary.
- Library search treats startup argument files specially and checks reduced names before returning an opened file.
- `file_prepare_stream()` copies the C file name into the stream buffer; too-long names relative to buffer size produce `limitcheck`.
- Closing a filter stream also disables and optionally frees temporary underlying streams.

## Research Notes
This is the central file object infrastructure used by the interpreter, filters, startup library loading, and IODevices.
