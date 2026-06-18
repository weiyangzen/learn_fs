# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_bmap.c

## Purpose

Implements UDFS logical-to-physical block mapping and extent allocation for file data. It maintains the in-core `icb_ext` extent arrays, reads continuation allocation descriptors, converts embedded files to normal allocation descriptors when needed, creates page-aligned holes, allocates/free-space-backed extents, and zero-fills new disk blocks.

## Main Entry Points

- `ud_bmap_has_holes()`: loads all allocation descriptors through file size and reports whether any extent is unrecorded/unallocated.
- `ud_bmap_read()`: maps a file offset to a device block and contiguous byte count, returning `UDF_HOLE` for unallocated extents.
- `ud_bmap_write()`: ensures backing storage exists for a write or allocation-only growth request, including embedded-to-short-ad conversion and sparse-hole handling.
- `ud_read_icb_till_off()`: follows continuation allocation extents until the in-core extent list covers a target offset.
- `ud_last_alloc_ext()`, `ud_create_ext()`, `ud_break_create_new_icb()`: grow, split, and append allocation descriptors.
- `ud_zero_it()`: writes zeros directly through `bdev_strategy()` to newly allocated blocks.

## Control Flow And State

`ud_bmap_write()` is the central allocator and expects `i_contents` held for writing. For `ICB_FLAG_ONE_AD`, it leaves small embedded writes in-place, but converts to `ICB_FLAG_SHORT_AD` once the request no longer fits in `i_max_emb`; it preserves previous embedded data through `fbread()`, allocates an extent array, and rolls back descriptor type, allocations, and memory if conversion fails. For non-embedded files it first calls `ud_read_icb_till_off()` so continuation descriptors are present in memory, then either extends the last extent or allocates holes/blocks inside existing unallocated extents.

Extents are capped by `MEXT_BITS` and rounded by logical-block and page boundaries. Holes are represented with `IB_UN_RE_AL` and are intentionally page-aligned where possible. When allocated extents can be adjacent to the previous extent and do not exceed maximum extent size, the code coalesces them; otherwise it splits the current extent and records a new physical allocation.

Continuation descriptors are tracked in `i_con`, read by `ud_read_next_cont()`, and expanded into `i_ext` by `ud_common_ad()` for both short and long allocation descriptors. `ud_bump_ext_count()` grows the in-core extent array and, when the file entry cannot hold more descriptors, allocates new continuation extent blocks and adjusts `i_cur_max_ext`.

## Dependencies

Depends on UDFS inode fields, allocation-descriptor formats, logical block size shifts, free-space allocator APIs (`ud_alloc_space()`, `ud_free_space()`), descriptor verification in `ud_verify_tag_and_desc()`, partition translation in `ud_xlate_to_daddr()`, and VM/fbuf interfaces for embedded-data and page-boundary behavior.

## Risks

The code is sensitive to byte/block rounding and extent array indexes. Several paths update in-core extents before all I/O succeeds, so rollback correctness matters for embedded-file conversion and partial allocations. `ud_break_create_new_icb()` computes the next physical block with shift/operator precedence that must be preserved intentionally. `ud_zero_it()` bypasses normal buffer-cache lifetime assumptions because reused freed space must not retain stale data.
