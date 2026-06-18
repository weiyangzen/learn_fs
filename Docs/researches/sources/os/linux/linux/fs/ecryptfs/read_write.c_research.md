# File Research: sources/os/linux/linux/fs/ecryptfs/read_write.c

Provides lower-file read/write primitives and a page-oriented high-level write path for eCryptfs.

Key behavior:
- `ecryptfs_write_lower()` writes bytes to the lower file with `kernel_write()` and marks the eCryptfs inode dirty.
- `ecryptfs_write_lower_page_segment()` maps a folio locally and writes a segment to the corresponding lower-file offset.
- `ecryptfs_write()` fills holes with zeros, copies caller data into eCryptfs folios, encrypts pages when required, or writes lower page segments for unencrypted files.
- Updates the eCryptfs inode size and encrypted-file size metadata when writes extend the file.
- Aborts long writes if a fatal signal is pending.
- `ecryptfs_read_lower()` wraps `kernel_read()` on the lower file.
- `ecryptfs_read_lower_page_segment()` maps a folio, reads lower bytes into it, and flushes D-cache state.

Important interactions:
- Assumes each eCryptfs inode private object has a valid `lower_file`.
- Used by address-space operations and metadata-writing paths in `mmap.c`.
- Preserves the split between logical upper offsets and physical lower-file storage.
