# File Research: sources/local-fs/udftools/mkudffs/file.c

Implements mkudffs file, directory, extended-attribute, and allocation helpers.

Descriptor tagging:
- `query_tag` computes descriptor tags for existing `udf_desc` objects, including CRC and tag checksum.
- `udf_query_tag` computes a descriptor tag from raw components and a data list.

Directory/FID insertion:
- `insert_desc` appends a FID payload to a directory, either in-ICB or through short/long allocation descriptors.
- `insert_fid` builds a File Identifier Descriptor, sets ICB references, copies unique ID low bits into allocation descriptor implementation-use data, updates link counts, and updates parent sizes.
- `compute_ident_length` pads FID length to a four-byte boundary.

File/data creation:
- `insert_data` appends data to in-ICB FE/EFE files and updates information/object sizes.
- `udf_create` allocates blocks, creates FE or EFE descriptors, initializes timestamps and unique IDs, sets file type/flags, inserts into parent directories, and increments LVID file/dir counters.
- `udf_mkdir` wraps `udf_create` for directories and creates the unnamed parent backlink entry.

Extended attributes:
- `insert_ea` adds ECMA extended attributes in the required ordering groups: ECMA-defined, implementation-use, and application-use.
- It creates the EA header when needed, maintains implementation/application attribute offsets, handles UDF 1.50 offset semantics, and retags the EA header.

Allocation helpers:
- Implements bit scanning helpers for UDF space bitmaps.
- `udf_alloc_bitmap_blocks` finds aligned free runs in bitmap descriptors and clears bits to allocate.
- `udf_alloc_table_blocks` consumes or splits short allocation descriptors in unallocated/freed space tables.
- `udf_alloc_blocks` updates LVID free-space count and dispatches allocation through freed bitmap/table, unallocated bitmap/table, or VAT append mode.

Key role: constructs the file-tree-level UDF metadata used for root directories, VAT files, stream-like objects, and allocation accounting.

Notable details:
- Supports both FE and EFE paths behind `FLAG_EFE`.
- Supports strategy 4096 by allocating two blocks and using strategy type 4096 metadata.
- Allocation failures are fatal.
