# File Research: sources/virtualization/nbdkit/plugins/floppy/floppy.c

This is the nbdkit plugin entry point for serving a host directory as a read-only virtual FAT32 floppy-like disk image.

Key behavior:
- Parses `dir`, `label`, and optional `size` parameters.
- Initializes and frees a global `struct virtual_floppy`.
- In `.get_ready`, calls `create_virtual_floppy` to scan the directory and construct all virtual disk regions.
- Exposes `.get_size`, `.block_size`, `.can_multi_conn`, `.can_cache`, and `.pread`.

Read path:
- `floppy_pread` repeatedly finds the virtual region covering the current offset.
- `region_file` opens the corresponding host file, reads from the adjusted offset, and closes it.
- `region_data` copies from in-memory metadata buffers.
- `region_zero` fills with zeroes.

Integration:
- Delegates all FAT32 layout work to `virtual-floppy.c` and directory entry work to `directory-lfn.c`.
- Uses `regions.h` for sparse virtual disk layout.
- Advertises parallel thread model and multi-connection safety because the generated image is immutable after `.get_ready`.

Risks and edge cases:
- Host files are reopened on each file-region read segment, which is simple but can be costly.
- Files changing after `.get_ready` could invalidate stored size/metadata assumptions.
- Only a single `dir` is accepted; a TODO mentions future multi-directory merging.
