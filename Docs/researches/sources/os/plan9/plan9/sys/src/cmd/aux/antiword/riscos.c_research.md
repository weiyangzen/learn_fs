# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/riscos.c

This file implements RISC OS platform services used by Antiword.

Key behavior:
- `werr()` reports errors through DeskLib and exits on fatal severities.
- `iGetFiletype()` and `vSetFiletype()` read and set RISC OS file types through `OS_File`.
- `bMakeDirectory()` verifies or creates the directory portion of a dotted RISC OS path.
- Reads current alphabet and OS version through SWIs.
- In debug builds, `bGetJpegInfo()` queries JPEG metadata through the JPEG module.

Important details:
- Filetype-setting ignores expected read-only media errors.
- Directory parsing uses the last `.` as the directory/file separator.

Filesystem relevance:
- Direct platform filesystem support for RISC OS file metadata and directory creation.
