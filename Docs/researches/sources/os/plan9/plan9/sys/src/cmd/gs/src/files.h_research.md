# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/files.h

Interpreter support declarations for PostScript file objects.

Key points:
- Defines `fptr` and `make_file` for refs that wrap Ghostscript streams.
- Declares lazy stdio accessors `zget_stdin`, `zget_stdout`, `zget_stderr`, and `zis_stdin`.
- Defines `ref_stdin`, `ref_stdout`, and `ref_stderr` access macros.
- Documents the read/write ID scheme used to detect closed or reused stream objects.
- Provides validation macros for file refs:
  - `check_file`
  - `check_read_file`
  - `check_read_known_file`
  - `check_write_file`
  - `check_write_known_file`
- Declares mode switching helpers `file_switch_to_read` and `file_switch_to_write`.
- Declares library/file open helpers, stream filter opening, stream-backed file ref creation, close helpers, stream allocation, `zreadline_from`, line editing, and stdio-needed pseudo-operators.

Dependencies and interactions:
- Used by interpreter file, filter, IODevice, and main argument modules.
- Depends on Ghostscript `stream`, `ref`, VM memory, IODevice, and file path abstractions.

OS/filesystem relevance:
- This is the central interpreter contract between PostScript file objects and Ghostscript streams/IODevice-backed file access.
