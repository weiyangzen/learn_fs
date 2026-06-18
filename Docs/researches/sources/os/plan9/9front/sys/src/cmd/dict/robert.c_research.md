# File Research: sources/os/plan9/9front/sys/src/cmd/dict/robert.c

Adapter for Robert Électronique dictionary data.

Key elements:
- Defines a 256-entry byte-to-rune/control table for Robert source encoding.
- Handles citation pointers, style controls, symbol/font controls, superscript, and subscript.
- `robertindexentry` decodes pointer records into definition and etymology offsets/lengths, reads auxiliary files, and delegates formatting.
- `robertprintentry` renders definition/etymology text, inline citations, baseline changes, and newline behavior.
- `citation` reads citation records from `cits.rob`.
- `robertnextoff` advances fixed-size pointer records by 16 bytes.
- `robertprintkey` streams `/lib/dict/robert/_phon`.
- `robertflexentry` handles verb-form data from `flex.rob`; `robertnextflex` uses `$` separators.
- `Bouvrir` opens Robert auxiliary files and exits with a French error message on failure.

Dependencies:
- Uses additional Robert data files: `cits.rob`, `defs.rob`, `etym.rob`, `_phon`, and pointer/flex files from `utils.c`.

Research notes:
- Main dictionary entries are indirect: the indexed file stores pointers to separate definition/etymology/citation files.
