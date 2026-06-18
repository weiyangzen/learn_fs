# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.c

Read completely: 128 lines.

This module implements a no-op iconv converter that copies bytes from input to output. Shared and per-context initialization store no closure. `convert` copies `min(*inbytes, *outbytes)` bytes, updates byte counts, reports zero invalids, and returns `E2BIG` if output space was insufficient.

Important interactions: exports iconv getops via `_CITRUS_ICONV_DEF_OPS(iconv_none)` and `_citrus_iconv_none_iconv_getops`.

Security/reliability notes: the copy itself is bounded by `len`. However, the pointer advancement in `_citrus_iconv_none_iconv_convert` uses `in += len` and `out += len`, which advances the local pointer-to-pointer variables rather than `*in` and `*out`. The byte counters are decremented, but caller-visible buffer pointers are not advanced. This looks like a functional bug with possible retry-loop consequences for callers expecting normal iconv pointer updates.
