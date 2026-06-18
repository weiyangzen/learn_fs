# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srdline.h

Interface declaration for Ghostscript readline support.

Key contents:
- Defines `sreadline_proc` signature for reading a prompted line from an input stream to a growable buffer.
- Documents buffer-growth behavior, EOL handling, `^M`/`^J` suppression via `pin_eol`, and `is_stdin` callback use.
- Declares the default implementation `sreadline`.

Notable dependencies:
- Requires `gsmemory.h` and `gstypes.h` according to the header comment.
- Uses opaque `stream`.

Research notes:
- This file contains only the interface contract; implementation is elsewhere.
