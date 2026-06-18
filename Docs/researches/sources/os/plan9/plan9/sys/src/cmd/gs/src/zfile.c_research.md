# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfile.c

## Purpose
Implements non-I/O PostScript file operators, file-name parsing, library-path file opening, safe-mode permission checks, temp-file handling, and low-level file stream allocation/closing.

## Key Functions
- `zfile()` opens files or IODevices, including special `%statementedit%` and `%lineedit%` handling.
- `zdeletefile()`, `zrenamefile()`, and `zstatus()` implement file-control/status operators.
- `zfilenameforall()` enumerates matching files via IODevice callbacks.
- `zexecfile()` executes a file and guarantees close through e-stack cleanup.
- `zlibfile()` searches the Ghostscript library path.
- `ztempfile()` creates scratch files with restricted prefix/absolute-path checks.
- `parse_file_name()`, `parse_real_file_name()`, and `parse_file_access_string()` validate file operands.
- `file_alloc_stream()`, `file_close_file()`, and `file_close()` manage stream lifetime and reuse.

## Important Behavior
- Stream objects carry serial ids; closing increments ids so stale PostScript file objects cannot access reused streams.
- Safe mode blocks `%pipe%` and applies permit-list matching after path reduction.
- Temp files created by `.tempfile` are allowed selected control operations through `SAFETY/tempfiles`.
- Library search checks reduced names before returning an opened file.

## Research Notes
This is the central file object infrastructure used by the interpreter, filters, startup library loading, and IODevices.
