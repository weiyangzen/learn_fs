# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclio.h

Defines the command-list I/O abstraction used by both filesystem-backed and RAM-backed clist storage implementations.

Key behavior:
- Defines opaque `clist_file_ptr`.
- Declares open/close/unlink operations; empty filename on write mode requests generated scratch storage, while empty filename on read mode is invalid.
- Declares `clist_space_available`, raw byte write/read functions, memory-warning threshold setup, error-code reporting, tell, rewind, and seek.
- Documents that `clist_ferror_code` returns Ghostscript-style error codes, with `0` for no error and `1` for low-memory warning.
- Passes filenames to rewind/seek because some implementations may need to close and reopen storage.

Dependencies:
- Includes `gp.h` for `gp_file_name_sizeof`; uses Ghostscript memory, bool, and integer types from surrounding common headers.

Research notes:
- Compile/link selection chooses the concrete implementation, allowing the same command-list code to target embedded RAM storage or external files.
- The API exposes low-memory warning semantics even though the filesystem implementation treats them as no-ops.
