# File Research: sources/virtualization/libguestfs/lib/whole-file.c

Trusted local whole-file reader.

Important behavior:
- Opens a local file read-only with CLOEXEC.
- Uses `fstat` to size the file, allocates `size + 1`, and reads until the expected byte count is reached.
- Treats premature EOF as an error.
- Closes the descriptor and reports close failures.
- NUL-terminates the returned buffer for caller convenience without counting the NUL in `size_r`.
- Explicitly documents that this is only for regular, local, trusted files because untrusted files can cause denial of service.

Filesystem relevance:
- Utility for reading trusted host-side metadata/configuration files into memory during libguestfs operations.
