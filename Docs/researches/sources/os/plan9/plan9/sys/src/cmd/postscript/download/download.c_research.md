# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.c

Host-resident PostScript font downloader/filter.

Key responsibilities:
- Reads a font map table mapping PostScript font names to host files.
- Optionally reads resident-font lists and marks those fonts already present.
- Scans input PostScript for `%%DocumentFonts:` and continuation comments.
- Copies required mapped font files to stdout before the input file.
- Handles stdin through a temporary copy when scanning ahead.
- Supports options for comment name, forced full scan, map name, printer/resident list, host font directory, temp directory, debug, and ignore-fatal mode.

Important behavior:
- Map-file comments begin with `%`.
- Relative font file paths are resolved under `hostfontdir`.
- Fonts are downloaded only once per process.
- `(atend)` causes full scanning.

Dependencies:
- Uses common `comments.h`, `gen.h`, `path.h`, `ext.h`, and `download.h`.

Notable risks:
- It assumes PostScript files in one invocation are part of a single job.
- Temporary-file handling uses `tempnam()`.
- Map parser relies on `strtok()` over a full in-memory file.
