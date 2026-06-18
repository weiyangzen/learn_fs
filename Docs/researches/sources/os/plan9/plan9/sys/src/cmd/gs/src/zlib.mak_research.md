# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zlib.mak

Partial Ghostscript makefile for building or linking zlib. It expects the including make system to define source, generated, object, and zlib-sharing variables such as `GSSRCDIR`, `ZSRCDIR`, `ZGENDIR`, `ZOBJDIR`, `SHARE_ZLIB`, and `ZLIB_NAME`.

The makefile defines zlib source/object path macros, zlib-specific compile flags, clean targets, and generated `.dev` module targets. When `SHARE_ZLIB=1`, encoder/decoder/crc modules are emitted as library dependencies on `ZLIB_NAME`. When `SHARE_ZLIB=0`, it compiles bundled zlib sources and creates `zlibc.dev`, `zlibe_0.dev`, `zlibd_0.dev`, and `crc32_0.dev`.

It covers common code (`zutil`), compression (`adler32`, `deflate`, `compress`, `trees`, `crc32`), and decompression (`inffast`, `inflate`, `inftrees`, `uncompr`, with older zlib 1.1.x source lists retained). The comments document supported zlib versions and warn about older zlib bugs/security issues.
