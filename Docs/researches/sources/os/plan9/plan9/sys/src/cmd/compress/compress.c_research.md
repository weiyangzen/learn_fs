# File Research: sources/os/plan9/plan9/sys/src/cmd/compress/compress.c

Classic Unix `compress`/`uncompress`/`zcat` implementation using Welch LZW compression with variable-width codes and optional block-compression table resets.

The main path parses traditional flags (`-b`, `-c`, `-d`, `-f`, `-n`, `-v`, `-V`, `-C`), recognizes invocation name to select decompression or zcat behavior, writes/reads the `0x1f 0x9d` magic header, and chooses smaller hash-table sizes for small input files. Compression uses open-addressed double hashing over prefix/character pairs, increases code width from 9 bits up to `maxbits`, and emits `CLEAR` when adaptive compression ratio worsens. Decompression rebuilds the string table on the fly and handles the KwKwK special case.

The file overlays compression hash storage with decompression prefix/suffix/stack tables to save memory. File metadata is copied to generated `.Z` output by `copystat`, but the original input unlink is commented out in this Plan 9 copy. It uses POSIX-style stdio/stat/signal/utime headers rather than native Plan 9 `bio`.
