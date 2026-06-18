# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/riscos.c

RISC OS platform support layer.

Key responsibilities:
- Implements `werr()` using DeskLib error reporting.
- Gets and sets RISC OS filetypes through `OS_File`.
- Creates missing output directories for RISC OS path syntax.
- Reads the current alphabet number and RISC OS version through SWIs.
- In debug builds, queries JPEG metadata through `JPEG_Info`.

Important behavior:
- Fatal `werr()` exits; nonfatal calls only report warnings.
- `vSetFiletype()` silently tolerates common read-only media errors.
- `bMakeDirectory()` treats the part before the last dot as the directory name.

Dependencies:
- DeskLib `Error`, `SWI`, RISC OS SWIs, Antiword shared constants.

Research relevance:
- Isolates RISC OS-specific system integration from the portable document parser.
