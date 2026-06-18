# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.h

Data definitions and compatibility macros for LZ4 compressor support.

Defines:
- Big-endian swap macros for v1 and v2 option structs.
- Stream format `LZ4_LEGACY`.
- Flags `LZ4_HC`, `LZ4_NON_DEFAULT`, `LZ4_FLAGS_MASK`.
- Default acceleration `LZ4_ACC_DEFAULT`.
- `struct lz4_comp_opts_v1` and `struct lz4_comp_opts_v2`.

Library-version compatibility:
- For `LZ4_VERSION_NUMBER >= 10700`, uses `LZ4_compress_fast()` and `LZ4_compress_HC()`, default HC level 12.
- For older libraries, uses older limited-output APIs, default HC level 9, and defines runtime guards for unsupported acceleration.

Notable typo:
- Comment says “omly legacy stream format”.
