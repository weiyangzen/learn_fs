# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/example.c

## Purpose
Sample and regression test program for the vendored zlib API.

## Key Elements
Tests `compress`/`uncompress`, gzip file I/O, small-buffer deflate/inflate, large-buffer compression with dynamic parameter changes, full flush and `inflateSync`, and preset dictionary deflate/inflate.

## Behavior/Risks
The program exits on first failure through `CHECK_ERR` or explicit validation checks. It creates a gzip test file named `foo.gz` or platform variant, corrupts part of a compressed stream to test sync recovery, and verifies preset dictionary IDs via Adler-32. It allocates large cleared buffers so repeated data compresses predictably.

## Dependencies
Uses public `zlib.h`, standard C I/O/string/allocation headers where available, gzip APIs, deflate/inflate APIs, and filesystem access for the gzip test file.
