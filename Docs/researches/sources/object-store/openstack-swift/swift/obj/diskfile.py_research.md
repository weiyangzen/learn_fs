# sources/object-store/openstack-swift/swift/obj/diskfile.py

## Purpose
`diskfile.py` is Swift's reference object-storage backend for POSIX filesystems. It defines the diskfile abstraction used by the object server to create, read, update metadata for, delete, audit, replicate, and reconstruct object data. It also owns the on-disk naming format, extended-attribute metadata format, quarantine mechanics, suffix hashing, async-update persistence, and separate replicated versus erasure-coded policy behavior.

The module's public backend contract is represented by `DiskFile`, `DiskFileWriter`, and `DiskFileReader`. `DiskFileManager` and `ECDiskFileManager` are reference implementation managers that encode policy-specific behavior and are used through storage-policy dispatch.

## Important APIs, Types, And Functions
Directory helpers `get_data_dir()`, `get_async_dir()`, and `get_tmp_dir()` map a policy or policy index to policy-suffixed directory names such as `objects`, `objects-<N>`, `async_pending`, and `tmp`. Metadata helpers `_encode_metadata()`, `_decode_metadata()`, `_read_file_metadata()`, `read_metadata()`, and `write_metadata()` serialize object metadata as pickle protocol 2 in one or more xattrs under `user.swift.metadata*`, with a separate metadata checksum under `user.swift.metadata_checksum`.

Hash and cleanup helpers include `read_hashes()`, `write_hashes()`, `consolidate_hashes()`, `invalidate_hash()`, `valid_suffix()`, and `quarantine_renamer()`. These maintain `hashes.pkl` and `hashes.invalid`, track suffix invalidations for replication, and move corrupt hash or suffix directories to `quarantined/<objects-dir>/...`.

`AuditLocation` and `object_audit_location_generator()` supply auditor scan locations without selecting a specific `.data` file. `get_auditor_status()`, `update_auditor_status()`, and `clear_auditor_status()` persist auditor partition cursors in JSON status files.

`DiskFileRouter` builds one policy-specific manager per configured storage policy. `BaseDiskFileManager` implements shared manager behavior: config parsing, mount checks, suffix hashing, replication and partition locks, async pending pickle writes, diskfile construction, audit-location conversion, hash iteration, and object lookup by hash. Subclasses implement `_process_ondisk_files()`, `_update_suffix_hashes()`, and `_hash_suffix()`.

`BaseDiskFileWriter` manages temporary file creation, allocation/free-space checks, chunk writes, periodic `fdatasync`, metadata xattr writes, `fsync`, buffer-cache dropping, atomic publish via rename or `O_TMPFILE` link, suffix invalidation, obsolete-file cleanup, and partition-power relinking cleanup. `DiskFileWriter.put()` finalizes replicated `.data` writes. `ECDiskFileWriter.put()` writes fragment-index metadata and defers cleanup; `ECDiskFileWriter.commit()` renames a non-durable EC fragment to a durable filename.

`BaseDiskFileReader` provides WSGI-compatible iteration, range iteration, multi-range iteration, optional cooperative yielding, optional zero-copy `splice()` send, cache dropping, length/etag validation, and quarantine on read mismatch or EIO. `ECDiskFileReader` extends it with pyeclib fragment metadata/checksum validation.

`BaseDiskFile` represents one object path or hash directory. It opens the current valid on-disk file set, reads and merges `.data` and fast-POST `.meta` metadata, validates name/hash/content length/expiration, returns metadata and readers, creates data/meta/tombstone files, and raises Swift diskfile exceptions for missing, deleted, expired, corrupt, or colliding objects. `DiskFile` is the replicated-policy subclass. `ECDiskFile` adds fragment preferences, durable-fragment reporting, fragment maps, and `purge()` for reconstructor handoff cleanup.

`DiskFileManager` implements replicated file-set selection and suffix hash updates. `ECDiskFileManager` implements EC filename parsing/formatting, fragment-index validation, durable-fragment selection, fragment preference handling, EC-specific file-set verification, per-fragment suffix hashes, and EC suffix hashing.

## Control Flow
Object writes start with `BaseDiskFile.create()`, which yields a writer. `BaseDiskFileWriter.open()` creates either an unnamed `O_TMPFILE` in the target data directory or a named file in the policy temp directory, then checks/reserves space. `write()` streams bytes, updates the upload md5, and periodically syncs and drops cache. `put()` computes the final policy-specific filename from `X-Timestamp`, optional content-type timestamp, and optional EC fragment index; writes metadata to xattrs; fsyncs file data and metadata; invalidates the suffix hash; atomically publishes the file; optionally hard-links to the next partition-power path; then cleans obsolete files.

For replicated policies, a single newest `.data` file defines object existence, newer `.meta` files define fast-POST metadata, and `.ts` files define deletion when newer than data. For EC policies, `.data` filenames include `#<frag_index>` and may include `#d` to mark durability. EC PUT is two-phase: `put()` writes a non-durable fragment and `commit()` renames it to the durable filename. Legacy `.durable` files are still recognized.

Object reads start with `BaseDiskFile.open()`. It lists the hash directory, asks the subclass manager to choose a valid file set, raises `DiskFileNotExist` or `DiskFileDeleted` when no data file is usable, opens the selected data file, reads xattr metadata, reads any `.meta` files, merges immutable datafile metadata back over fast-POST metadata, validates the object name and directory hash, checks `X-Delete-At`, verifies content length against `fstat()`, and returns itself as a context manager. `reader()` transfers file-handle ownership to a reader object. The reader validates full-object length and optionally etag when a read starts at offset zero and reaches EOF; EC readers also validate fragment metadata at fragment boundaries.

Diskfile cleanup and replication hashing run through `cleanup_ondisk_files()`, `get_ondisk_files()`, and `_hash_suffix_dir()`. `get_ondisk_files()` parses filenames, sorts by timestamp, marks obsolete entries, retains the newest metadata and content-type metadata combinations, delegates policy-specific data-file selection, and returns chosen files plus obsolete or reclaimable candidates. Cleanup removes reclaimable tombstones and obsolete files and removes empty hash directories. Hashing walks suffix directories, cleans object directories, updates md5 state from meaningful object-state timestamps and extensions, and writes stable suffix hashes while using invalidation files and locks to avoid racing with writers.

Audit flow enters through `object_audit_location_generator()` or manager wrappers. It yields hash-directory paths by device, policy datadir, partition, suffix, and object hash, persisting partition progress into `auditor_status_<type>.json`. The auditor later converts each location into a diskfile with `from_hash_dir()`, causing metadata names to be read and checked against the hash directory.

## State, Persistence, And Dependencies
Object data is persisted as files under `<devices>/<device>/<objects-dir>/<partition>/<suffix>/<hash>/<timestamp...>.<ext>`. Replicated policy uses `.data`, `.meta`, and `.ts`. EC policy uses fragment-indexed `.data` files with optional durable markers and may see legacy `.durable` files. Metadata is persisted in extended attributes as pickled dictionaries, with a metadata checksum xattr for corruption detection and optional modernization to add missing checksums. Tombstones are zero-length temp-published files with `X-Timestamp` metadata.

Replication state is persisted in `hashes.pkl` and `hashes.invalid` in each partition. Async container-update retries are pickled under `async_pending[-policy]/<suffix>/<hash>-<timestamp>`. Audit scan state is JSON in policy data directories. Quarantine moves directories into the device's `quarantined` area and invalidates suffix hashes. Temporary writes use the policy temp directory or unnamed temp files linked into place.

Dependencies include POSIX filesystem semantics, xattrs, `fcntl`, `O_TMPFILE`/linkat support when available, Swift utility functions for hashing, locking, timestamp encoding, pickle IO, fsync/fdatasync, fallocate and free-space checks, storage policy definitions, Swift diskfile exception classes, `pyeclib` for EC validation, eventlet `tpool` and trampoline support, and Swift's multi-range response iterator.

## Integration Points
The object server calls manager `get_diskfile()` to service PUT, GET, HEAD, POST, and DELETE. Replicator and reconstructor call `get_hashes()`, `yield_hashes()`, `replication_lock()`, `partition_lock()`, `get_diskfile_from_hash()`, EC `purge()`, and EC fragment/durable metadata properties. The auditor calls `object_audit_location_generator()` and `get_diskfile_from_audit_location()`. Container-update retry code depends on `pickle_async_update()`. Storage policies select `DiskFileManager` versus `ECDiskFileManager`, and the in-memory backend in `mem_diskfile.py` duck-types a smaller version of this contract.

Metadata merge behavior integrates directly with Swift fast-POST semantics: immutable datafile metadata such as content length, deleted marker, etag, object sysmeta, and selected system metadata override user-updated `.meta` values, while content-type timestamp handling allows content type to be replicated independently from other metadata updates.

## Risks
The module relies on subtle filesystem guarantees. Bugs in rename/linkat ordering, fsync coverage, xattr writes, or hash invalidation can surface as lost writes, stale replication hashes, or inconsistent reads. `O_TMPFILE` fallback is global to the manager (`use_linkat`), so one unsupported target disables that path for later writes. Metadata pickle reading must tolerate old Python 2/3 encoding differences while avoiding checksum false positives.

On-disk file-set selection is complex, especially for EC: tombstones, `.meta` files, durable and non-durable fragments, legacy `.durable`, fragment preferences, reclaim age, and commit-window behavior interact. Small changes can cause a node to serve a non-durable fragment, incorrectly hide metadata, or prematurely reclaim data needed by reconstruction. `get_ondisk_files()` explicitly raises if the policy-specific contract is violated, which is good for detection but sensitive to edge-case regressions.

Reader-side quarantine can happen during response iteration or zero-copy send after the object server has begun streaming. Tests must account for exceptions after headers may have been prepared. EC fragment validation warns rather than quarantines for some `ECDriverError` cases, while invalid metadata/checksums quarantine; this distinction affects operational behavior.

Concurrency is lock-based and race-aware but necessarily best-effort. Hash writes compare the current `hashes.pkl` to an original snapshot and recurse on races. Audit and cleanup tolerate disappearing files by translating them to state-change or not-exist errors. Partition-power relinking introduces another path where failed hard links or cleanup can leave duplicate or stale files until later cleanup.

## Test Signals
Strong tests should cover metadata xattr round trips, metadata checksum addition and mismatch quarantine, old encoding decode paths, no-xattr and no-space error translation, policy directory naming, filename parse/format for replicated and EC policies, suffix invalidation consolidation, hash-cache race handling, quarantine moves, audit-location cursor files, and async pending pickle paths.

Diskfile behavior tests should cover PUT/read/delete lifecycles, fast-POST metadata merging, content-type timestamp precedence, tombstone precedence, expired objects with and without `open_expired`, name/hash mismatch collision handling, malformed metadata quarantine, missing/corrupt directories, cleanup of obsolete files after reclaim age, reader length/etag quarantine, range and multi-range iterators, and zero-copy send checksum paths when supported.

EC-specific tests should cover fragment-index validation, non-durable write followed by durable commit, legacy `.durable` recognition, durable fragment set selection, fragment preferences including explicit empty lists, fragment map reporting, suffix hashes by fragment index, EC reader fragment metadata validation, and `purge()` cleanup for handoff fragments and tombstones.

No local tests were present under the vendored source tree, so these signals are derived from the code's contracts and expected Swift upstream test boundaries such as object server, replicator/reconstructor, diskfile, and auditor suites.
