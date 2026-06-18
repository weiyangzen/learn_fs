# File Research: sources/os/plan9/plan9/sys/src/cmd/page/page.c

Main entry point for the `page` document/image viewer. It parses global flags, sniffs input type, initializes the appropriate `Document`, starts the draw display, and enters `viewer`.

Supported options include resizing/new-window behavior, reverse order, PPI, bounding-box handling, image-only mode, debug verbosity, Ghostscript teeing, abort-on-note, and antialias bits. With no files and non-image mode, stdin is duplicated and `/dev/cons` replaces fd 0 for interaction.

File type detection uses the first 16 bytes to select PDF, PostScript/PJL, DVI, Microsoft Office, troff output, or graphics. Unrecognized input falls back to graphics conversion.

The file also manages a note watcher. Non-`die` notes are forwarded to the process group; alarms from Ghostscript trigger group termination. `wexits` coordinates shutdown and watcher cleanup.
