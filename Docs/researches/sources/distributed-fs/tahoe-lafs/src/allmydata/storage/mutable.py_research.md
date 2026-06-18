# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/mutable.py

## Purpose
Implements the filesystem-backed mutable share container. `MutableShareFile` owns the Tahoe mutable share layout: fixed header, write enabler, data length, lease area, share payload, and extra lease records. It provides the low-level storage operations behind mutable slot reads, test-and-write updates, lease renewal, and lease cancellation.

## Important APIs, Types, And Functions
`MutableShareFile` exposes `create()`, `unlink()`, `readv()`, `writev()`, `get_length()`, `check_write_enabler()`, `check_testv()`, `add_lease()`, `renew_lease()`, `add_or_renew_lease()`, `cancel_lease()`, and `get_leases()`. Important internal helpers include `_read_share_data()`, `_write_share_data()`, `_change_container_size()`, `_read/write_data_length()`, `_read/write_extra_lease_offset()`, `_read/write_lease_record()`, `_enumerate_leases()`, and `_get_first_empty_lease_slot()`. `EmptyShare` evaluates test vectors against absent shares, `testv_compare()` implements the only supported test operator, and `create_mutable_sharefile()` creates then reopens a share.

## Control Flow
Construction reads the header of an existing file and selects a schema with `schema_from_header()`, or uses the newest schema for new files. `create()` writes a versioned empty header. Reads clamp requested ranges to the current data length. Writes may first move the extra lease block beyond newly expanded data, fill holes with zero bytes, update the recorded data length, and then write the payload. Slot-level compare-and-swap is supported by `check_testv()` followed by `writev()` in `StorageServer`.

## State And Persistence
All durable state is embedded in the share file. The first four leases are fixed-size slots in the header region and further leases live after share data. The code deliberately does not shrink container allocation when data shrinks; it only lowers the logical data length. `_change_container_size()` copies the extra lease block, zeros the old block, and updates the offset, but comments identify interrupt windows that can corrupt leases.

## Dependencies And Integration Points
This module integrates with `storage.server` mutable slot APIs, `mutable_schema` for versioned headers and lease serializers, `LeaseInfo` for lease records, `MAX_MUTABLE_SHARE_SIZE` for size limits, `timing_safe_compare` for write-enabler checks, and Tahoe interface exceptions such as `BadWriteEnablerError`, `NoSpace`, and `DataTooLargeError`.

## Risks And Test Signals
High-risk behavior includes crash consistency around lease-block movement, write ordering when data length is increased before data bytes are written, sparse-write hole filling, no-op container shrinkage, and hashed versus cleartext lease compatibility. Tests should exercise read truncation, write expansion, zero-filled holes, max-size rejection, v1/v2 header recognition, wrong write enabler logging, lease add/renew/cancel, zero-length share deletion through server write vectors, and interrupted or corrupted header handling.
