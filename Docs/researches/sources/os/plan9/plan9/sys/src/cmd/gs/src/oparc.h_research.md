# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/oparc.h

`oparc.h` declares Ghostscript arc operator procedures: `zarc`, `zarcn`, and `zarct`.

The header notes these declarations live separately from `opextern.h` because arc operators are not included in PDF-only configurations. It depends on `i_ctx_t` being visible from the including interpreter headers.

This is a small interpreter interface boundary for optional PostScript path operators.
