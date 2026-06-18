# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.h

This is the public libbzip2 API header.

Contents:
- Action constants: `BZ_RUN`, `BZ_FLUSH`, `BZ_FINISH`.
- Return/status constants: `BZ_OK`, `BZ_STREAM_END`, `BZ_PARAM_ERROR`, `BZ_MEM_ERROR`, `BZ_DATA_ERROR`, and others.
- `bz_stream` structure with input/output pointers, availability counters, total counters, opaque state, and allocator hooks.
- Export/API macros for Windows and non-Windows builds.
- Prototypes for low-level compression/decompression APIs.
- Prototypes for buffer-to-buffer convenience APIs.
- Prototype for `BZ2_bzlibVersion`.

Notable implementation details:
- Header says it is modified from the original bzip2 distribution, mainly split into smaller pieces.
- It excludes many higher-level stdio APIs; those live in separate stdio headers.
