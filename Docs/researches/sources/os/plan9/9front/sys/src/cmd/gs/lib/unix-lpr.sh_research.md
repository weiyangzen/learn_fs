# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/unix-lpr.sh

Unix lpr filter script for routing print jobs through Ghostscript.

Main behavior:
- Defines Ghostscript executable and search paths, exports `PATH`, `LD_LIBRARY_PATH`, and accounting variables.
- Redirects stdout to stderr for logging and preserves original stdout on fd 3 for raw printer data.
- Parses lpr filter arguments for user (`-n`), host (`-h`), and accounting file.
- Derives filter name, device, and queue type (`direct` or `indirect`) from its symlink path.
- Parses device suffixes for colors and bits-per-pixel.
- Logs job metadata using spool lock/control-file data.
- For direct queues, sends Ghostscript output to fd 3 via `cat`; for indirect queues, pipes to `lpr -P${device}.raw`.

Filtering pipeline:
- `gsif` passes input through.
- `gsnf` uses `psdit`; `gstf` uses `pscat`; `gsgf` uses `psplot`; `gsvf` uses `rasttopnm | pnmtops`; `gsdf` uses `dvi2ps -sqlw`.
- Unsupported `gscf`/`gsrf` print an error and exit.
- Appends PostScript accounting code that records page count, host, and user.
- Runs Ghostscript with `-q -dNOPAUSE -sDEVICE=${device} -dBitsPerPixel=${bpp}` and optional color count.

Filesystem relevance:
- Print spool/filter integration script that reads lpr metadata, writes accounting, and routes output. It touches spool paths but is not filesystem implementation code.
