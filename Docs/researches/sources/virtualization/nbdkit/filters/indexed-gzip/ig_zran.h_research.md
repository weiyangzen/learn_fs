# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.h

Declares the nbdkit-specific zran wrappers. Defines `Z_NBDKIT_ERROR` as a custom negative return code outside normal zlib error values.

Documents `ig_deflate_index_build()` as the nbdkit-backed equivalent of `deflate_index_build()`, taking `nbdkit_next`, filter handle, span, and nbdkit error pointer. Documents `ig_deflate_index_extract()` as the `next->pread()`-based equivalent of zran extraction.

This header separates original zran data structures from nbdkit I/O adaptation.
