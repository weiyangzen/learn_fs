# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_handle.h

Defines the per-connection `struct handle` for the indexed gzip filter. It contains a `struct deflate_index *index` and cached `compressed_size`.

Includes zlib, nbdkit filter APIs, and common cleanup/pread/minmax helpers. This header is shared by the filter glue and custom zran functions so both can access the index and upstream compressed size.
