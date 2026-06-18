# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/directory_impl.py

## Purpose
This module is the local FoundationDB Python directory layer implementation vendored for the metadata audit tools. It maps human directory paths to binary key prefixes, allocates short unique prefixes under contention, supports directory creation/open/list/move/remove, and exposes opened directories as `Subspace` objects.

## Important APIs, Types, And Functions
`HighContentionAllocator.allocate()` chooses a unique tuple-packed integer prefix using counter windows under `hca` metadata, snapshot reads, no-conflict writes to recent candidate keys, and explicit write conflict keys for winners. `Directory` is the user-facing wrapper with transactional `create_or_open`, `open`, `create`, `list`, `move`, `move_to`, `remove`, `remove_if_exists`, and `exists` methods that delegate into a `DirectoryLayer`.

`DirectoryLayer` owns node metadata and implements `_create_or_open_internal`, `move`, `_remove_internal`, `list`, `exists`, `_find`, `_remove_recursive`, `_is_prefix_free`, and version initialization. `DirectorySubspace` combines content prefix packing with directory operations. `DirectoryPartition` creates a nested `DirectoryLayer` under a directory prefix and intentionally disables packing on the partition root. `_Node` caches metadata for lookup and partition dispatch.

## Control Flow
Opening or creating starts with `_check_version`, normalizes paths through `_to_unicode_path`, walks node metadata from the root via `_find`, and either returns existing contents, delegates into a partition, or allocates/writes a new node. Automatic prefix allocation uses `content_subspace.key() + allocator.allocate(tr)` and then checks both actual database keys and directory prefix metadata for collisions. Parent directories are created recursively through `create_or_open(path[:-1])` when needed.

Move validates that the destination is not a subdirectory of the source, resolves both endpoints, rejects cross-partition moves, writes the old node prefix into the new parent's subdir map, and removes the old parent entry. Remove recursively clears child nodes, clears all keys under the content prefix, and deletes node metadata.

## State And Persistence Behavior
Directory layer state is stored in system-neutral user keyspace: root node metadata under the default node subspace `b"\xfe"`, directory node metadata keyed by physical content prefix, child name-to-prefix mappings under subkey `0`, layer labels under `b"layer"`, and a packed version tuple in `b"version"`. Directory contents live at the allocated physical prefixes. Removing a directory clears both content data and metadata, but already-open clients can continue writing to the removed prefix because the returned subspace is just bytes.

The allocator stores counters and recent candidate markers under the root node's `b"hca"` subspace. It advances windows when counters show a window is more than half full, then suppresses some write conflict ranges while adding conflict only on the chosen candidate.

## Dependencies And Integration Points
The module depends on `fdb.impl.transactional`, `fdb.tuple`, and `Subspace`. It is a compatibility layer for Python bindings used by metadata scripts or other tools that expect `fdb.directory`. It integrates with tuple ordering for paths and prefix allocation, transaction conflict semantics for allocator correctness, and `impl.strinc` for prefix-range checks.

## Risks And Edge Cases
This is low-level prefix management: manual prefixes can overlap real data if `_allow_manual_prefixes` is enabled or if callers supply stale prefixes. Recursive remove is destructive over the entire content prefix. Partition roots intentionally reject subspace packing, which can surprise code treating every directory as a key prefix. Prefix allocation depends on randomized retries and transaction conflict behavior; changes to no-conflict range semantics can break uniqueness assumptions. Version checks only guard major/minor directory layer compatibility, not schema corruption inside metadata keys.

## Test Signals
Useful tests cover creating/opening nested directories, layer mismatch rejection, automatic and manual prefix collision rejection, move within and across partitions, recursive remove clearing metadata and contents, allocator uniqueness under concurrent transactions, and path normalization from bytes/strings. Partition tests should verify delegation and root operation restrictions.
