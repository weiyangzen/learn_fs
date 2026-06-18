# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/minigzip.c

## Purpose
Example utility that simulates a small subset of gzip using zlib’s `gz*` API.

## Key Elements
Implements `gz_compress`, optional `gz_compress_mmap`, `gz_uncompress`, `file_compress`, `file_uncompress`, and `main`. Supports `-d`, compression strategies `-f`, `-h`, `-r`, and levels `-1` through `-9`.

## Behavior/Risks
Intended for testing, not as a full gzip replacement. File mode compresses to `<file>.gz` and unlinks the original after success; decompress mode removes the input gzip file. Uses fixed `MAX_NAME_LEN` buffers with `strcpy`/`strcat`, so very long names are unsafe. Pipe mode wraps stdin/stdout using `gzdopen`. Error handling is intentionally limited and exits the process on failure.

## Dependencies
Includes `zlib.h`, stdio, optional mmap/stat headers, and platform-specific binary-mode/unlink handling.
