# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.c

Main program for troff-to-PostScript translation. It parses options, loads device/font descriptions, converts input into a temporary PostScript body, then emits prologues/setup/font build snippets followed by the temporary body and trailer.

Key behavior:
- Option handling covers aspect ratio, copies, debug, magnification, forms-per-page, page list, landscape, offsets, and passthrough PostScript.
- Uses a temporary output file first so it can discover used draw support and build characters before writing final prologue.
- `prologues` emits DPOST prologue, optional draw prologue, rounded-page support, setup variables, Latin1 encoding, forms setup, and required charlib build procedures.
- Final phase copies temp body to stdout and calls `finish`.

Integration points:
- Calls `readDESC`, `conv`, `cat`, `finish`.
- Depends on global `drawflag` and `build_char_list` populated during conversion.

Risks:
- Uses `tmpnam`, which is race-prone in general.
- Temporary file cleanup is registered with `atexit`; abrupt termination can leave files.
- Many global state dependencies make conversion order important.
