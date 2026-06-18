# sources/distributed-fs/tahoe-lafs/src/allmydata/dirnode.py

## Purpose

This module implements Tahoe-LAFS directory nodes. A directory is backed by a file node whose contents serialize child names, read caps, encrypted write caps, and metadata. The module supports metadata updates, child add/delete/set/move operations, immutable-directory packing, recursive traversal, manifests, deep stats, and deep check/repair.

## Important APIs, Types, And Functions

Eliot fields and `ADD_FILE` instrument file additions. `update_metadata()` preserves Tahoe system metadata and updates link creation/modification times. Modifier classes `Deleter`, `MetadataSetter`, and `Adder` implement callbacks passed to mutable file `modify()`. `_encrypt_rw_uri()`, `pack_children()`, and `_pack_normalized_children()` serialize children and optionally superencrypt write caps. `DirectoryNode` implements `IDirectoryNode`, `ICheckable`, and `IDeepCheckable` with methods for reading/listing, child lookup, metadata, setting caps/nodes, uploading files, deleting, creating subdirectories, moving children, and deep traversal. `ManifestWalker` extends `DeepStats`; `DeepChecker` collects check/repair results.

## Control Flow

Reads call `_read()`, which downloads the backing mutable/immutable file and unpacks netstring entries. Unpacking normalizes names, decrypts write caps only for writable directories, strips padding spaces, constructs child nodes through the nodemaker, validates constraints, and caches packed entries in `AuxValueDict`. Mutations create a modifier object and pass its `modify()` method to the backing mutable file node, which reads old contents, edits the child map, repacks bytes, and publishes the new version. `add_file()` uploads content before linking the resulting node. Deep traversal is a strict depth-first Deferred chain that tracks verifier caps to avoid loops and processes file-like children before directories to reduce memory.

## State And Persistence

Persistent directory state is the packed backing file contents: sorted netstring child entries with UTF-8 names, readonly caps, encrypted write-cap data, and JSON metadata. Write caps are encrypted with a key derived from the directory writekey and a salt derived from the child write cap; a legacy MAC is appended for older readers. Runtime state includes the backing node, wrapped directory URI, nodemaker, uploader, traversal monitor, found verifier set, and result aggregators.

## Dependencies And Integration Points

The module integrates with AES helpers, hash/base32 utilities, mutable and immutable file nodes, unknown nodes, Tahoe interfaces/errors, check result classes, monitors, upload consumers, URI wrapping, netstring/json utilities, Eliot tracing, Twisted Deferreds, Foolscap scheduling, and deep stats.

## Risks

Serialization compatibility is critical; changing netstring order, metadata JSON, cap stripping, or writecap encryption would affect all directories. AES-CTR leaks encrypted writecap length as noted in comments. Assertions enforce many invariants but can be disabled. Move is implemented as set in destination then delete from source, with comments in SFTP noting possible data-loss windows for path moves. Deep traversal is intentionally serial and may be slow on huge trees, though it avoids high memory use. Duplicate verifier caps are skipped, which can under-count multiply linked objects.

## Test Signals

Round-trip pack/unpack across mutable and immutable directories, Unicode normalization, metadata timestamp preservation, no-write readonly wrapping, add/set/delete/move semantics with overwrite modes, encrypted writecap decryptability, deep-immutable constraint failures, traversal loop avoidance, manifest contents, deep stats counters, and deep check/repair aggregation.
