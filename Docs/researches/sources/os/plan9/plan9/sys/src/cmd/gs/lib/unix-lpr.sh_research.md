# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/unix-lpr.sh

Unix BSD `lpr` filter script for Ghostscript-rendered printer queues.

Key behavior:

- Sets search paths for Ghostscript, PBMPLUS, PostScript filters, and X11 libraries.
- Redirects stdout to stderr for logging while preserving file descriptor 3 for raw printer output.
- Parses lpr filter arguments for user, host, and accounting file.
- Infers filter name, device name, and direct/indirect queue type from `$0` path layout created by `lprsetup.sh`.
- Parses optional device suffixes for colors and bits-per-pixel.
- Logs job metadata using the spool lock/control file.
- Chooses output strategy:
  - `direct`: pipe rendered bytes to fd 3,
  - `indirect`: pipe rendered bytes to `lpr -P${device}.raw`.
- Filters input through format-specific preprocessors based on filter name (`gsif`, `gsnf`, `gstf`, `gsgf`, `gsvf`, `gsdf`).
- Appends PostScript accounting code that records page count, host, and user.
- Runs Ghostscript with `-sDEVICE`, `-dBitsPerPixel`, optional color count, and `-sOutputFile=|...`.

This is legacy Unix print-spool integration. It is operational shell code but outside Plan 9 filesystem research scope.
