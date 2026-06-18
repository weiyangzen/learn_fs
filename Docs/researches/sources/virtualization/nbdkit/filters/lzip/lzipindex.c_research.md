# File Research: sources/virtualization/nbdkit/filters/lzip/lzipindex.c

Implements the lzip member index. Members are appended as they are discovered while scanning from archive end toward start, so the stored vector is in reverse file order.

`lzip_index_finalize()` walks the reverse vector back into logical order, assigns each member’s uncompressed `data_offset`, sums `combined_data_size`, and determines whether all non-final data blocks have a uniform `indexable_data_size`.

`lzip_index_search()` uses constant-time indexing when `indexable_data_size` is nonzero; otherwise it uses the generated vector binary-search helper with a comparator that maps an uncompressed offset into a member range.

`lzip_index_destroy()` resets the vector and zeroes the structure.
