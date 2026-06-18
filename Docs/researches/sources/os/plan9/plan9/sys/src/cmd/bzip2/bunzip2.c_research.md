# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bunzip2.c

Plan 9 `bunzip2` frontend using the embedded libbzip2 stream API.

Options:

- `-c`: write decompressed output to stdout.
- `-v`: libbzip2 verbosity.
- `-D`: increments a debug flag.

For files, it verifies the `BZh` magic, derives output names by stripping `.bz2` or mapping `.tbz`/`.tbz2` to `.tar`, refuses unsafe overwrite cases, then streams through `BZ2_bzDecompressInit`, `BZ2_bzDecompress`, and `BZ2_bzDecompressEnd`.

Uses Plan 9 `Biobuf` for buffered I/O and removes a partially written output file on failure.
