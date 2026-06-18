# File Research: sources/os/plan9/plan9/sys/src/cmd/tar.c

Plan 9 `tar` implementation supporting create, append/update, table-of-contents, and extract modes. It targets POSIX `ustar` for extraction and, by default, creation, while retaining compatibility with older tar headers and GNU/FreeBSD binary large-size fields.

Key structures and constants:
- `Hdr` is a 512-byte tar header union with POSIX `ustar` extension fields.
- `Compress` maps suffixes to compression/decompression filters: gzip, compress, bzip2.
- `Pushstate` tracks forked compression filter processes.
- Archive data is buffered in `nblock` groups of 512-byte `Tblock`s, defaulting to 20 blocks.

Main behavior:
- `main` parses tar keyletters with a custom `TARGBEGIN`, then dispatches to `replace` for `c/r` or `extract` for `x/t`.
- `replace` creates or updates an archive, optionally pushes a compressor, recurses directories through `addtoar`, and writes two zero end blocks.
- `extract` opens an archive, auto-detects decompression by suffix or `-z`, reads headers with checksum validation, matches path prefixes, and calls `extract1`.
- `readhdr`, `hdrsize`, `arsize`, and `chksum` handle header validation, size decoding, and stream resync with `-s`.

Notable details:
- Large file sizes are emitted in GNU-style base-256 binary form when `dir->length >= 1<<32`.
- Extraction refuses to create hard links, symlinks, and FIFOs, printing diagnostics instead.
- Relative extraction is default; `-R` preserves absolute/device-like names.
- `-i` attempts to ignore read errors by zero-filling unread blocks and seeking past errors when possible.
- `skip` and `refill` optimize skipping large members on seekable archives.

Dependencies:
- Plan 9 libc APIs: `Dir`, `dirreadall`, `dirfstat`, `dirfwstat`, `create`, `cleanname`, `seek`, `wait`, `fork`, `execl`.
- `<fcall.h>` for `%M` directory mode formatting.
- `<String.h>` Plan 9 string builder routines.
