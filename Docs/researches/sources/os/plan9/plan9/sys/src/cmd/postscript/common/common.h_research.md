# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.h

Plan 9-oriented shared declarations for PostScript translators.

Key responsibilities:
- Defines rune helper macros, `BOOLEAN`, and true/false constants.
- Declares common translator globals such as `programname`, `inputfilename`, page counters, current font, and position.
- Declares `Biobufhdr` stdout/stderr handles.
- Defines `strtab` and declares `charcode`.
- Prototypes page/string/output helpers, allocation, field parsing, and page-list handling.

Notable behavior:
- This header overlaps conceptually with `gen.h`/`ext.h` but is for the Plan 9/Bio-based translator path.
