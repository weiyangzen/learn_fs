# sources/storage-engines/rocksdb/util/crc32c_ppc_constants.h

Purpose: shared CRC-32C polynomial definitions and lookup/reduction constants for PPC C and assembly paths.

Important definitions: sets `CRC` to `0x1edc6f41`, enables `REFLECT` and `CRC_XOR`, provides `crc_table[]` when `CRC_TABLE` is defined for scalar alignment/tail work, and otherwise emits assembly labels `.constants`, `.short_constants`, and `.barrett_constants`.

Control flow: under non-assembly C usage it provides only the 256-entry table. Under `__ASSEMBLY__` it emits MAX_SIZE and long constant tables for reducing 262144 kbits to 1024 bits, final short reductions, and reflected Barrett constants.

State and persistence: no mutable state. Constants are algorithmic state: any change alters CRC results and breaks compatibility.

Dependencies and integration: included by `crc32c_ppc.c` with `CRC_TABLE` and by `crc32c_ppc_asm.S` with `__ASSEMBLY__`.

Risks: dual C/assembly behavior makes accidental macro changes dangerous. The tables are hard to audit manually; endian/reflection assumptions must stay in sync with assembly.

Test signals: generic CRC vectors and PPC execution are the primary validation signals.
