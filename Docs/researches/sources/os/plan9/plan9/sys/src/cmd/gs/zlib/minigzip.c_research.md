# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/minigzip.c

## Purpose
Small example/test implementation of a gzip-like command using zlib’s `gz*` API. It is explicitly not intended as a full gzip replacement.

## Main Functions
- `error(msg)`: prints program-prefixed error and exits.
- `gz_compress(in, out)`: streams input `FILE *` to `gzFile`.
- Optional `gz_compress_mmap(in, out)`: compresses an mmap’d file when `USE_MMAP` is enabled.
- `gz_uncompress(in, out)`: streams `gzFile` to output `FILE *`.
- `file_compress(file, mode)`: writes `<file>.gz`, then unlinks the original.
- `file_uncompress(file)`: expands `.gz` input or appends `.gz` to locate input, then unlinks compressed input.
- `main(argc, argv)`: parses `-d`, `-f`, `-h`, `-r`, and `-1`..`-9`.

## Behavior
With no file arguments, it reads stdin and writes stdout, using `gzdopen()` over the existing descriptors. With file arguments, it creates/removes files similarly to basic gzip behavior.

## Portability
Contains platform branches for binary mode on DOS/Windows/Cygwin, VMS/RISC OS suffix behavior, optional mmap, and compiler-specific `fileno` handling.

## Limitations and Risks
The source comments warn that error checking is limited and filesystem naming constraints are not handled. `file_compress` and `file_uncompress` use fixed `MAX_NAME_LEN` buffers with `strcpy`/`strcat`, making it test/demo code rather than hardened utility code.
