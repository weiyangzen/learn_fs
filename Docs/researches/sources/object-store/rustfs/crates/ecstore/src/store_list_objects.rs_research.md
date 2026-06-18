# sources/object-store/rustfs/crates/ecstore/src/store_list_objects.rs

## Purpose

Implements ECStore object listing and walking for S3 ListObjectsV2, ListObjectVersions, internal `list_path`, and streaming `walk_internal`. It fans out over erasure pools/sets/disks, reads metacache entries, merges sorted channels, resolves metadata by quorum, and converts entries to `ObjectInfo` results.

## Important APIs and Types

`ListPathOptions` carries bucket, prefix, base dir, marker/cache id, separator, limit, quorum mode, deletion/version flags, recursion, transient cache behavior, and pool/set cursor fields. Main APIs are `ECStore::inner_list_objects_v2`, `list_objects_generic`, `inner_list_object_versions`, `list_path`, `walk_internal`, `SetDisks::list_path`, `max_keys_plus_one`, marker parse/encode helpers, `gather_results`, and `merge_entry_channels`.

## Control Flow

ListObjectsV2 chooses continuation token or `start_after`, then delegates to generic listing. Generic listing caps max keys at 1000, requests one lookahead entry, may optimize exact single-key `max_keys == 1` with `get_object_info`, calls `list_path`, converts metacache entries to objects, separates common prefixes for delimiter listings, and computes truncation/next markers. Version listing adds version-marker parsing and can include the marker entry when a key marker plus version marker is supplied.

`list_path` validates arguments, normalizes marker/prefix/separator/recursive options, parses RustFS cache marker tags, computes `base_dir`, sets transient mode for reserved/invalid buckets, then spawns producer `list_merged` and consumer `gather_results` tasks connected by Tokio channels and a cancellation token. `list_merged` starts `SetDisks::list_path` per set and merges their channels. `SetDisks::list_path` chooses disks from `RUSTFS_API_LIST_QUORUM` mode, computes metadata resolution quorum, and calls `list_path_raw`.

`merge_entry_channels` is a k-way sorted merge that deduplicates names, merges version metadata for matching object entries via `merge_file_meta_versions`, and respects cancellation during receive/send. `walk_internal` streams latest-only or all-version `ObjectInfoOrErr` values to callers and reduces set errors with `walk_result_from_set_errors`.

## State and Persistence Behavior

The file does not persist durable state directly. It reads disk/metacache state and may assign reusable listing ids for non-transient truncated listings. `Unexpected` is used as an EOF sentinel, while `err == None` from `gather_results` means the requested limit was filled.

## Dependencies and Integration Points

Depends on bucket argument validation, versioning config, `rustfs_filemeta`, `list_path_raw`, `SetDisks`, disk info/error types, object-info conversion, Tokio channels/tasks, cancellation tokens, UUIDs, RustFS path helpers, and tracing.

## Risks and Edge Cases

The EOF/full-limit convention is subtle and can break truncation if misinterpreted. Delimiter collapse re-evaluates truncation after object/common-prefix separation. The merge assumes sorted inputs. `auto` quorum depends on mutation counters and falls back if no quorum disk set exists. Version-marker semantics only apply when the key-marker entry is present.

## Test Signals

In-file tests cover gather limit return, marker inclusion/skipping, version-marker gating, max-key lookahead, list quorum env parsing, metadata resolver version limits, null/UUID version markers, cache marker round trips, walk error reduction, sorted/deduped merge output, and cancellation cases.
