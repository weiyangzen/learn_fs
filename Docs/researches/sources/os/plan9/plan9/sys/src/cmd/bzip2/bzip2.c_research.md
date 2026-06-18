# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2.c

Plan 9 `bzip2` frontend using the embedded libbzip2 stream API.

Options:

- `-1` through `-9`: compression level, default `6`.
- `-c`: write compressed output to stdout.
- `-v`: libbzip2 verbosity.
- `-D`: increments a debug flag.

Rejects directories, derives output names as `.bz2` or `.tbz` for `.tar`, and streams input through `BZ2_bzCompressInit`, repeated `BZ2_bzCompress`, and `BZ2_bzCompressEnd`. Uses a one-extra-loop flush hack to drain the output buffer after stream end.
