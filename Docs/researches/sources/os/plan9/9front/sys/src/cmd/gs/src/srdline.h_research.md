# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/srdline.h

Declares the readline interface used by Ghostscript streams.

Key points:
- Defines the `sreadline_proc` signature for reading a line from an input stream with prompt output.
- Supports continuing into an existing buffer at `*pcount`.
- Allows buffer reallocation through `bufmem` when the line exceeds available space; returns 1 instead if no buffer memory is supplied.
- Tracks CR/LF folding through `*pin_eol`, allowing a following LF after CR to be discarded.
- Accepts an `is_stdin` callback for a special condition in the default implementation.
- Declares the default `sreadline`.

Research relevance:
- Small API header for line-oriented input on top of Ghostscript streams.
