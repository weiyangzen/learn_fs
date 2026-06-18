# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzbuffcompress.c

This is another copy of `BZ2_bzBuffToBuffCompress`.

Behavior:
- Validates input/output pointers and compression parameters.
- Defaults work factor to 30 when zero.
- Initializes stream compression, runs `BZ_FINISH`, finalizes state, and updates destination length on success.
- Returns libbzip2 status codes such as `BZ_PARAM_ERROR`, `BZ_OUTBUFF_FULL`, or the compression error code.

Relationship:
- The contents match `buffcompress.c` in this group, suggesting alternate build naming or duplicate split-library packaging.
