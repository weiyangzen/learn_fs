# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.h

Shared definitions for the `download` font downloader.

Key responsibilities:
- Defines `Map`, which maps a PostScript font name to a host file and tracks whether it has already been downloaded.
- Declares `allocate()` for growing map arrays.
