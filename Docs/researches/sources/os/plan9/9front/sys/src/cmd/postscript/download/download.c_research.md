# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.c

`download.c` prepends host-resident font files to PostScript jobs based on DSC font comments. It reads a font-name-to-file map, optionally marks printer-resident fonts as already downloaded, scans `%%DocumentFonts:` or another configured comment, handles continuation comments and `(atend)`, and copies mapped font files once before the original input.

For stdin, it uses a temporary file to preserve scanned input before copying the complete stream. Options configure comment keyword, forced full scan, map name, printer/resident list, host font directory, temp directory, debug, and fatal-error handling.
