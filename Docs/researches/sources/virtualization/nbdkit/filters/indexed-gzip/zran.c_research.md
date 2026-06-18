# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/zran.c

Contains shared zran support code and optional standalone test harness. The active production functions manage `struct deflate_index` allocation, access-point growth, freeing, and binary serialization/deserialization.

`deflate_index_free()` frees every point dictionary, list, reusable inflate stream, and index object. `add_point()` grows the point list geometrically, captures compressed input location, uncompressed output location, bit offset, dictionary length, and saved sliding window.

`deflate_index_serialize()` writes raw `int`, `off_t`, metadata, and window bytes. `deflate_index_deserialize()` reads that format, initializes a raw inflate stream, validates coarse bounds such as mode and point count, allocates points, and restores dictionaries.

Under `#ifdef TEST`, the file includes a command-line demo that can build/load an index and extract bytes from a local file.
