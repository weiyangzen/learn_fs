# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_sparse.c

Read completely. This file implements sparse-file related FSCTLs and a sparse-preserving copy helper.

`smb2_fsctl_set_sparse()` toggles `FILE_ATTRIBUTE_SPARSE_FILE`, requiring a regular file and at least one of write attributes, write data, or append data access. It reads current DOS attributes and writes updated attributes only when a change is needed.

`smb2_fsctl_set_zero_data()` decodes a signed start/end range, validates ordering and regular-file status, requires write-data access, clamps zeroing to EOF, checks byte-range lock conflicts, and calls `smb_fsop_freesp()` to create holes or free space.

`smb2_fsctl_query_alloc_ranges()` validates the requested signed range, requires read-data access, clamps to EOF, and returns allocated regions. Non-sparse files return one allocated range. Sparse files use `smb_fsop_next_alloc_range()` to walk data/hole extents and encode ranges until output space is exhausted.

`smb2_sparse_copy()` is shared by copychunk and ODX. It walks source allocated ranges, punches holes in the destination for source gaps, then reads and writes allocated data with a caller-provided buffer. It preserves sparseness where possible and falls back to normal copying when allocation-range queries are unsupported.

`smb2_fsctl_query_file_regions()` implements Hyper-V-style valid-data/file-region reporting. It validates optional input, requires output space for the fixed header plus one region, reads file size and DOS attributes, and encodes hole/data region entries with total and returned counts. If output space is insufficient it returns buffer overflow after reporting partial region counts.
