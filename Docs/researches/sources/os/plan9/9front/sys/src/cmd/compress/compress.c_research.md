# File Research: sources/os/plan9/9front/sys/src/cmd/compress/compress.c

Historical Unix `compress`/`uncompress`/`zcat` implementation using LZW compression, adapted for Plan 9 APE via `_PLAN9_SOURCE` and standard C/POSIX headers.

Command behavior is selected by program name or flags. Supports compression, decompression, stdout mode, force overwrite, max bits via `-b`, no-magic legacy mode, quiet/verbose stats, and optional debug table/code dumping when compiled with `DEBUG`.

Compression uses variable-width LZW codes from 9 up to `maxbits` default 16, open-addressed double hashing over prefix+character pairs, optional block compression with `CLEAR`, adaptive table reset when compression ratio worsens, and file-size-tuned hash table sizes.

Decompression reconstructs the LZW string table on the fly using overlaid memory: compression hash table storage doubles as decompression prefix/suffix/stack storage.

File lifecycle: for named files it writes `.Z` output or strips `.Z` on decompression, prompts before overwrite in foreground, copies mode/owner/timestamps to output, and unlinks unsuccessful output. The input unlink is commented out in this 9front copy, so successful compression does not remove the source.

Important caveats: old C style in debug helpers, many globals, fixed output filename buffer, legacy signal handling, and classic `compress` format constraints rather than modern compression/container design.
