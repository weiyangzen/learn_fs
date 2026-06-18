# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/tdef.h

Read fully: 674 lines, 18401 bytes. SHA-256 prefix: `2aa89e43962c9104`.

This is troff’s central private definition header. It establishes site paths, default device names, starting typesetting parameters, array limits, internal control characters, Tchar bit layout, block-based macro/string storage, and the main shared structures.

Key definitions:
- `Tchar` internal character/motion encoding, with `MOT`, `VMOT`, `NMOT`, `ZBIT`, size/font masks, and `cbits`/`sbits`/`fbits` helpers.
- Internal control characters such as `DRAWFCN`, `XON`, `XOFF`, `WORDSP`, `HX`, `FLSS`, and motion marker `MOTCH`.
- Storage types `Blockp`, `Diver`, `Stack`, `Contab`, `Numtab`, `Env`, `Font`, `Chwid`, `Term`, and `Numerr`.
- Environment-field macros mapping names like `pts`, `font`, `line`, `word`, `tabtab`, and `lss` into `envp`.
- Device/font constants and limits such as `NCHARS`, `MAXFONTS`, `NTAB`, `NDI`, `NTRTAB`, and buffer sizes.

Integration: included by the troff implementation files and tightly coupled to matching environment layout in initialization code.

Risk notes: comments explicitly warn that `struct Env` must stay synchronized with `ni.c`.
