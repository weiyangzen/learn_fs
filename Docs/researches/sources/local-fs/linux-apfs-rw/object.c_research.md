# File Research: sources/local-fs/linux-apfs-rw/object.c

## Purpose

`object.c` implements APFS object checksum handling, checkpoint-map construction, checkpoint ring index helpers, ephemeral-object lookup, and copy-on-write mapping for non-ephemeral object blocks.

## Main Flows

- `apfs_fletcher64()` computes the APFS object checksum over 32-bit little-endian words, assuming APFS block-size bounds keep accumulator growth safe.
- `apfs_obj_verify_csum()` skips verification for buffers already in the active transaction because their checksum may be stale until commit.
- `apfs_multiblock_verify_csum()` and `apfs_multiblock_set_csum()` verify or set checksums for single-block and multi-block objects after the checksum field.
- `apfs_create_cpm_block()` initializes a checkpoint mapping block, joins it to the current transaction, marks it for checksum, and fills its object header with the current container xid.
- `apfs_create_cpoint_map()` appends a checkpoint mapping entry for an ephemeral object, returning `-ENOSPC` if the mapping block is full.
- `apfs_index_in_data_area()` and `apfs_data_index_to_bno()` convert between block numbers and current checkpoint data-ring positions.
- `apfs_ephemeral_object_lookup()` searches the in-memory ephemeral-object list by oid.
- `apfs_read_object_block()` reads a non-ephemeral object, verifies checksums when node checking is enabled, and performs CoW on write if the object belongs to an older transaction.

## Copy-On-Write Behavior

`apfs_read_object_block()` is the central non-ephemeral object CoW helper. On write, if the object's xid already matches the current container xid, the old buffer is reused. Otherwise, it allocates a new block, copies the old data, queues the old block for freeing unless `preserve` is true, updates physical object oid and xid, joins the new buffer to the transaction, and marks it for checksum.

The `preserve` path is used when the old object remains reachable, such as for snapshots. For preserved non-volume-superblock objects, the volume allocation counters are incremented because CoW adds a live block without freeing the old one.

## Integration Points

This file ties together checksum policy, checkpoint map generation, spaceman block allocation, transaction buffer tracking, and APFS physical/virtual object identity. It is used by transaction checkpoint writes, volume/omap/catalog mapping, snapshot creation, and btree/node update paths.

## Invariants And Risks

- Fletcher checksums assume APFS block sizes are small enough for the simplified implementation.
- Transaction buffers can have stale checksums until final commit.
- Ephemeral object count is fixed by the in-memory list limit elsewhere.
- CoW callers must choose `preserve` correctly or they can either leak accounting or free blocks still needed by snapshots.
- Failure after in-memory allocation changes relies on transaction abort forcing the container read-only rather than rolling back all in-memory state.

## Test Focus

Test checksum verification/set behavior, CoW of physical and virtual objects, preserved versus non-preserved writes, checkpoint-map capacity handling, checkpoint data-ring wraparound, and read-only failure paths after allocation or transaction-join errors.
