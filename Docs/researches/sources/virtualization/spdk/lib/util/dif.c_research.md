# File Research: sources/virtualization/spdk/lib/util/dif.c

This file implements SPDK DIF/DIX protection information utilities. It supports 16-bit, 32-bit, and 64-bit PI formats; DIF types 1, 2, and 3; interleaved metadata; separate metadata buffers; streaming partial-block generation/verification; protection-information copy insertion/stripping; error injection; CRC32C update; and reference-tag remapping.

The file defines the private `struct spdk_dif` layouts for the three PI formats and a private `_dif_sgl` iterator used to walk or construct iovec arrays. The SGL helpers advance across fragmented iovecs, validate total length, test block-size alignment, append split ranges, and copy iterator state. Most public operations choose a fast whole-block path when every iovec length is a multiple of the relevant block size, and fall back to split helpers when a logical block crosses iovec boundaries.

`spdk_dif_ctx_init()` validates PI format, DIF type, metadata size, interleaved metadata geometry, and data-block alignment requirements. It computes `guard_interval`, reference-tag offset, initial guard seed, and remapped reference-tag state. `spdk_dif_ctx_set_data_offset()` and `spdk_dif_ctx_set_remapped_init_ref_tag()` update stream/reference mapping fields after initialization.

The guard path maps PI format to CRC algorithm: T10 DIF CRC16 for PI16, NVMe CRC32C for PI32, and NVMe CRC64 for PI64. `_dif_generate()` writes guard, application tag, and reference tag fields depending on enabled DIF flags. `_dif_verify()` checks guard, application tag mask, and reference tag, honoring ignore rules: type 1/2 ignore all checks when application tag is `0xffff`; type 3 ignores when application tag and reference tag are both ignore values.

The main DIF APIs are `spdk_dif_generate()`, `spdk_dif_verify()`, and `spdk_dif_update_crc32c()`. They operate on buffers where metadata is part of each block. Split variants carry guard state across fragmented block pieces and copy DIF bytes through a temporary `struct spdk_dif` when the DIF field itself crosses iovec boundaries.

The copy helpers cover host/device metadata conversion. `spdk_dif_generate_copy()` either inserts DIF into a bounce buffer when PRACT is not set or metadata size equals DIF size, or overwrites existing metadata while regenerating DIF. `spdk_dif_verify_copy()` either strips DIF into data-only iovs while verifying or verifies/copies full blocks depending on PRACT and metadata size. Disabled-DIF variants copy data while skipping or preserving metadata slots without checking PI fields.

DIX support handles data and metadata as separate iovecs. `spdk_dix_generate()` writes PI into the metadata iov, `spdk_dix_verify()` validates separate metadata, and `spdk_dix_inject_error()` can flip bits in metadata guard/application/reference fields or in data. DIX metadata is represented as a single iovec in the public API.

`spdk_dif_inject_error()` and `spdk_dix_inject_error()` randomly choose a block, byte range, and bit, then flip a bit in the requested PI/data field. The code reseeds `rand()` with `time(0)` per injection call, so repeated calls in the same second may not be statistically independent.

The streaming APIs support partial ranges over metadata-interleaved buffers. `spdk_dif_set_md_interleave_iovs()` maps a data range to iovecs that skip metadata holes. `spdk_dif_generate_stream()`, `spdk_dif_verify_stream()`, and `spdk_dif_update_crc32c_stream()` compute the full buffer range containing data plus metadata, process block fragments, and preserve `ctx->last_guard` across calls. `spdk_dif_get_range_with_md()` and `spdk_dif_get_length_with_md()` convert data-only offsets/lengths to metadata-inclusive ranges.

Reference-tag remapping is implemented for DIF and DIX through `spdk_dif_remap_ref_tag()` and `spdk_dix_remap_ref_tag()`. These optionally verify the existing reference tag, then rewrite it using `ctx->remapped_init_ref_tag`, preserving ignore semantics and DIF-disabled shortcuts.

Important invariants are geometry correctness, guard interval calculation, PI-format field offsets, endian conversion, reference-tag masks, SGL length validation before iteration, and preserving guard state for split/streaming operations. Changes here affect NVMe DIF/DIX data integrity paths directly.
