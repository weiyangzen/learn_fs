# sources/object-store/openstack-swift/swift/common/utils/__init__.py

## Purpose

This module is the broad compatibility and convenience surface for `swift.common.utils`. It re-exports selected helpers from the newer split modules (`base`, `config`, `libc`, `timestamp`, `ipaddrs`, and logging utilities), preserves older import paths used by Swift and third-party middleware, and defines many of Swift's core operational helpers in one place. The file covers logging/statistics adapter construction, hash-path setup, durable filesystem operations, lock management, daemon option parsing, request/path/header parsing, iterator wrappers, rate limiting, async green-thread helpers, recon cache persistence, namespace and shard-range models, partition/path utilities, package entry-point loading, systemd notification, and watchdog timeout scheduling.

## Important APIs, Types, And Functions

- Re-exported APIs include `md5`, `quote`, `split_path`, config parsers/validators, libc wrappers, timestamp helpers, and IP helpers. Many callers still import these names directly from `swift.common.utils`.
- Logging entry points are `_patch_statsd_methods()`, `get_logger()`, and `get_prefixed_logger()`, which return Swift log adapters patched with legacy StatsD-like methods.
- Hash and configuration globals include `HASH_PATH_SUFFIX`, `HASH_PATH_PREFIX`, `SWIFT_CONF_FILE`, `set_swift_dir()`, `validate_hash_conf()`, `validate_configuration()`, and `hash_path()`.
- Filesystem and durability helpers include `fs_has_free_space()`, `fallocate()`, `punch_hole()`, `fsync()`, `fdatasync()`, `fsync_dir()`, `mkdirs()`, `makedirs_count()`, `renamer()`, `link_fd_to_path()`, `write_file()`, `remove_file()`, `remove_directory()`, `is_file_older()`, `listdir()`, `ismount()`, and `ismount_raw()`.
- Locking and process helpers include `lock_path()`, `lock_file()`, `lock_parent_directory()`, `drop_privileges()`, `clean_up_daemon_hygiene()`, `parse_options()`, `get_hub()`, `get_pid_notify_socket()`, `NotificationServer`, `systemd_notify()`, `Watchdog`, `WatchdogTimeout`, and `get_ppid()`.
- Request and object-storage helpers include `generate_trans_id()`, `get_trans_id_time()`, `select_ip_port()`, `node_to_string()`, `storage_directory()`, `validate_device_partition()`, `validate_sync_to()`, `get_remote_client()`, `public()`, `private()`, `replication()`, `majority_size()`, `quorum_size()`, `rsync_ip()`, and `rsync_module_interpolation()`.
- Iterator, WSGI, and stream wrappers include `FileLikeIter`, `RateLimitedIterator`, `GreenthreadSafeIterator`, `CooperativeCachePopulator`, `AbstractRateLimiter`, `EventletRateLimiter`, `ContextPool`, `GreenAsyncPile`, `StreamingPile`, `ClosingIterator`, `ClosingMapper`, `CloseableChain`, `StringAlong`, `InputProxy`, `LRUCache`, `Spliterator`, and `CooperativeIterator`.
- Header and MIME helpers include `parse_content_range()`, `parse_content_type()`, `parse_header()`, `extract_swift_bytes()`, `override_bytes_from_content_type()`, `clean_content_type()`, `_MultipartMimeFileLikeObject`, `iter_multipart_mime_documents()`, `parse_mime_headers()`, `mime_to_document_iters()`, `maybe_multipart_byteranges_to_document_iters()`, `document_iters_to_multipart_byteranges()`, `document_iters_to_http_response_body()`, `multipart_byteranges_to_document_iters()`, and `parse_content_disposition()`.
- Namespace/sharding types are `NamespaceOuterBound`, `Namespace`, `NamespaceBoundList`, `ShardName`, `ShardRange`, and `ShardRangeList`, plus helpers `find_namespace()` and `filter_namespaces()`.
- Miscellaneous data helpers include `safe_json_loads()`, `strict_b64decode()`, `base64_str()`, `cap_length()`, `md5_hash_for_file()`, `get_partition_for_hash()`, `get_partition_from_path()`, `replace_partition_in_path()`, `load_pkg_resource()`, `round_robin_iter()`, `parse_override_options()`, `distribute_evenly()`, `get_redirect_data()`, `parse_db_filename()`, `make_db_file_path()`, and `get_db_files()`.

## Control Flow And Behavior

Import-time work loads the hash configuration lazily if `/etc/swift/swift.conf` exists, initializes split-module exports, defines global constants, and constructs lazy libc wrappers for `fallocate` and `posix_fallocate`. The module deliberately tolerates missing hash configuration at import time so tests and tools can monkey patch or call `set_swift_dir()` later.

`get_logger()` builds a Swift logger, creates a `StatsdClient`, attaches that client to the underlying core logger, then patches a legacy StatsD method interface onto the returned adapter. `get_prefixed_logger()` clones an adapter and reuses the original StatsD source when available, so callers can preserve metric emission while adding a log prefix.

Hash-path flow is global-state based. `set_swift_dir()` changes `SWIFT_CONF_FILE`, clears cached prefix/suffix bytes, and revalidates configuration. `validate_hash_conf()` reads `[swift-hash]` values with Latin-1 encoding, requiring at least one of suffix or prefix. `hash_path()` encodes account/container/object names, adds the configured secret bytes, and returns an MD5 hex digest or raw digest.

Filesystem write flow emphasizes durability. `renamer()` makes destination directories, retries after directory races, renames, then fsyncs the target leaf directory and each newly created parent directory. `link_fd_to_path()` links an unnamed or open fd via `/proc/self/fd/<fd>`, unlinks an existing target if needed, retries directory races, and optionally fsyncs directories. `fallocate()` validates offset/size, optionally enforces `FALLOCATE_RESERVE`, then calls Linux `fallocate`, POSIX `posix_fallocate`, or logs a one-time no-op warning if neither exists. `punch_hole()` requires Linux `fallocate` with `FALLOC_FL_PUNCH_HOLE`.

Lock flow uses eventlet-aware waiting. `lock_path()` creates one or more `.lock` files, tries non-blocking exclusive `flock()` across them, sleeps cooperatively until acquired or `LockTimeout` expires, and closes all lock fds on exit. `lock_file()` opens the lock target, acquires `flock()`, verifies the inode still matches the path to handle unlink/recreate races, yields a file object, optionally unlinks at the end, and retries if it detected a stale fd.

Stream and iterator helpers generally wrap existing iterables to add accounting, rate limiting, close semantics, cooperative sleeps, or file-like `read()`/`readline()` behavior. `GreenAsyncPile` and `StreamingPile` feed jobs into eventlet green pools and return results as they become available; exceptions inside jobs are converted to a private `DEAD` sentinel and skipped unless eventlet debug exception printing is enabled.

MIME/range flow parses and emits multipart bodies lazily. `iter_multipart_mime_documents()` checks the starting boundary, then yields `_MultipartMimeFileLikeObject` instances whose `read()`/`readline()` stop at boundaries. Higher-level helpers parse MIME headers into `HeaderKeyDict`, translate multipart byte ranges into body iterators, and construct single-part or multipart HTTP response bodies while preserving resource closure.

Namespace flow models object-name ranges as half-open/closed intervals `(lower, upper]`, with singleton minimum and maximum sentinels for outer bounds. `NamespaceBoundList` stores compact lower-bound/name pairs and recreates contiguous `Namespace` objects by using the next lower bound as the previous namespace's upper bound. `ShardRange` extends `Namespace` with persisted container-sharding state, conflict-resolution timestamps, object/byte/tombstone counters, deleted/reported flags, and state-machine constants. `ShardRangeList` adds aggregation and filtering convenience.

Watchdog flow centralizes many timeout expirations in one green thread. `Watchdog.start()` records timeout metadata keyed by object id and wakes the scheduler only when the new timeout expires earlier than the current next expiration. `Watchdog._run()` throws timeout exceptions into caller greenthreads through eventlet's hub when deadlines pass.

## State And Persistence

Persistent state touched by this module includes Swift config files, recon cache JSON files, object/account/container DB file names, device paths, lock files, mount marker stub files, systemd/Swift notification sockets, and process `/proc` metadata. Mutable module globals include hash prefix/suffix and config path, fallocate feature switches and warning state, lazy libc wrapper objects, and constants controlling drain/lock defaults. `CooperativeCachePopulator` also coordinates distributed state through memcached token and data keys. Namespace and `ShardRange` objects are serializable through `__iter__()` and `from_dict()` for database rows and JSON-like transport.

## Dependencies And Integration Points

The module depends on eventlet abstractions from `swift.common.concurrency`, logging classes from `swift.common.utils.logs`, `StatsdClient`, `HeaderKeyDict`, `swift.common.exceptions`, `swift.common.linkat`, timestamp helpers, config helpers, libc helpers, and IP helpers. It integrates with nearly every major Swift subsystem: account/container/object servers use `hash_path()`, `storage_directory()`, `config_true_value()`, durability helpers, and decorators; daemon and WSGI startup use `readconf()`, `modify_priority()`, `drop_privileges()`, and eventlet/log monkey patching; proxy controllers use range, multipart, close/drain, sharding, and redirect helpers; replicators, reconstructors, auditors, relinkers, and sharder code use device scanning, rate limiting, recon cache, namespace, and override parsing helpers. S3 middleware uses checksum-related imports from the sibling module and public decorators from this module.

## Risks And Edge Cases

- Importing this module has a wide blast radius because it is the historical `swift.common.utils` compatibility surface; behavior changes can affect out-of-tree middleware.
- Global hash configuration must be valid and stable. Changing `HASH_PATH_PREFIX/SUFFIX` changes ring/object placement hashes and can make existing data unreachable.
- Filesystem helpers depend on Linux-specific behavior such as `/proc/self/fd`, `O_TMPFILE`, fallocate flags, mount inode checks, and optional `.ismount` stubs. Portability and containerized mount detection are explicit risk areas.
- `fallocate()` error handling intentionally ignores unsupported-function errors but raises for other errno values. Incorrect errno handling can turn allocation failures into silent data-placement or ENOSPC issues.
- `lock_file()` and `lock_path()` rely on advisory locks and eventlet scheduling; misuse with non-cooperative code can still deadlock or starve.
- Multipart parsing is boundary-buffer based and caller-facing; malformed client input can produce `MimeInvalid` or `ChunkReadError`, while large or adversarial boundaries may stress buffering assumptions.
- `streq_const_time()` assumes string-like inputs whose elements can be passed to `ord()`. Passing bytes in Python 3 would produce ints and break.
- `LRUCache` stores state in the decorator instance and is not explicitly synchronized; shared use across native threads would be unsafe.
- `NamespaceBoundList.get_namespace()` assumes non-empty bounds and that the item maps at or after the first lower bound; bad or gapped inputs can map to the preceding namespace by design.
- `ShardRange` is mutable but intentionally hashable by identity despite equality comparing bounds, which is useful for internal maps but violates common hash/equality expectations.
- `Watchdog` uses eventlet hub internals and caller greenthread references; leaked or uncancelled timeouts can hold references and throw into unexpected greenthread lifecycles.

## Test Signals

The local OpenStack Swift snapshot under `sources/object-store/openstack-swift` does not include a `test` or `tests` tree, so no runnable in-repo tests were available for this research item. Strong expected coverage would include unit tests for hash config loading and `hash_path()`, fallocate and hole-punch error paths with mocked libc wrappers, lock race handling, recon cache atomic updates, MIME/range parser round trips, `LRUCache` timeout eviction, `Spliterator` slicing, namespace and shard-range ordering/serialization, systemd notification socket behavior, and watchdog timeout scheduling. Integration signals are widespread imports from account/container/object servers, proxy controllers, daemon/wsgi startup, sharder/reconciler/relinker, middleware, and CLI commands.
