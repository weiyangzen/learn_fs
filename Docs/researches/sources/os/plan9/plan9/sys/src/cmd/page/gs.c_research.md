# File Research: sources/os/plan9/plan9/sys/src/cmd/page/gs.c

Provides the Ghostscript process interface shared by PDF and PostScript backends. It spawns `/bin/gs` with the Plan 9 output device, pipes command input, captures intended bitmap data on fd 3, and monitors error output.

`spawngs` carefully reassigns low-numbered fds before exec, supports optional teeing of Ghostscript input, installs an `atexit` killer, initializes helper PostScript procedures, and stores fds in `GSInfo`.

`gscmd` writes formatted PostScript commands. `waitgs` synchronizes by asking Ghostscript to print a sentinel line and reading until it appears, treating lines containing `Error:` as fatal.

`setdim` configures resolution, page size, margins, optional bounding-box translation, and landscape rotation before a page is rendered.
