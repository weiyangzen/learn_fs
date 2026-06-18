# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclfile.c

Filesystem-backed implementation of the command-list I/O abstraction.

Key behavior:
- `clist_fopen` creates scratch files when passed an empty name for write modes, opens existing files otherwise, and rejects read mode with no filename.
- Uses Ghostscript platform wrappers for scratch-file and normal file opens.
- `clist_fclose` closes a file and optionally deletes it via `clist_unlink`.
- `clist_space_available` reports all requested space as available for file-backed storage.
- `clist_fwrite_chars` writes raw bytes with `fwrite`.
- `clist_fread_chars` uses direct `getc` fall-through for reads of 1 to 8 bytes to avoid inefficient tiny `fread` calls; larger reads use `fread`.
- Memory-warning threshold is a no-op in this implementation.
- `clist_ferror_code`, `clist_ftell`, `clist_rewind`, and `clist_fseek` wrap stdio status and positioning.
- `clist_rewind` can discard file data by reopening with write mode and then reopening with `w+` binary mode, working around the lack of portable stdio truncation.

Dependencies:
- Uses stdio, string, unlink wrappers, Ghostscript error/memory/platform headers, and the API contract from `gxclio.h`.

Research notes:
- The same `gxclio.h` interface can be backed by RAM storage on embedded systems; this file is the external filesystem variant.
- Return values from read/write are byte counts rather than normalized Ghostscript success/error codes, matching the clist I/O interface.
