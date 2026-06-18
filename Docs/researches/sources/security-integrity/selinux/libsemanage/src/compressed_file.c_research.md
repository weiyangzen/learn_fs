# sources/security-integrity/selinux/libsemanage/src/compressed_file.c

Purpose: centralizes reading, unmapping, and writing CIL/module files that may be bzip2-compressed.

Important APIs/types/functions: internal helpers `bzip` and `bunzip`; public/internal APIs `map_compressed_file`, `unmap_compressed_file`, and `write_compressed_file` over `struct file_contents`.

Control flow: mapping first tries to open and inspect the file, detects bzip magic, either memory-maps uncompressed files or decompresses streams into allocated memory, and records whether the data was compressed. Writing either writes raw bytes or compresses through libbz2 according to configuration on the handle.

State and persistence behavior: maps uncompressed files with `mmap` and stores decompressed content in heap memory. `unmap_compressed_file` chooses `munmap` versus `free` based on the `compressed` flag. Writes replace file contents at the requested path.

Dependencies and integration points: depends on bzlib, mmap, stdio, semanage config fields `bzip_blocksize`/`bzip_small`, and direct module install/extract code.

Risks: compressed and mapped lifetime paths differ; incorrect `compressed` bookkeeping causes invalid free/unmap. Decompression grows buffers dynamically and must guard allocation failure. Test signals include compressed/uncompressed round trips, zero-length files, corrupt bzip streams, and cleanup under failure.
