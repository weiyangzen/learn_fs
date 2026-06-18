# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.h

Internal header declaring the zlib fast inflate decoder.

Key responsibilities:
- Declares `inflate_fast(z_streamp strm, unsigned start)` with `ZLIB_INTERNAL` visibility.
- Documents that this header is internal implementation detail and not for applications.

Dependencies:
- Requires zlib stream types and `ZLIB_INTERNAL` to be defined before inclusion, normally through zlib utility/inflate headers.

Notable risks:
- The prototype exposes the fast decoder’s low-level entry point; callers must satisfy the assumptions documented in `hammer2_zlib_inffast.c`.
