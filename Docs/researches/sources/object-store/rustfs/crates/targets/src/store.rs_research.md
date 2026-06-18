## sources/object-store/rustfs/crates/targets/src/store.rs

Purpose: implements a filesystem-backed queue store used by notification targets to persist events or raw payloads for retry/replay. It supports single entries, concatenated JSON batches, raw bytes, optional Snappy compression, entry limits, oldest-first listing, and deletion.

Important APIs/types/functions: `Key` encodes UUID name, file extension, batch `item_count`, and compression flag into filenames like `3:<uuid>.json.snap`. `parse_key` reverses filenames into keys. `ensure_store_entry_raw_readable` probes a key and deletes unreadable entries except `NotFound`. `Store<T>` defines open/put/put_multiple/put_raw/get/get_multiple/get_raw/del/delete/list/len/is_empty/boxed_clone. `QueueStore<T>` implements the trait with `entries: RwLock<HashMap<String, i64>>`, `pending_entries: AtomicU64`, and `fs_guard`.

Control flow and state: `open` creates the directory, scans files, indexes modified times, and resets pending reservations. `put`, `put_multiple`, and `put_raw` acquire a filesystem read guard, reserve an entry slot by comparing `entries.len + pending_entries` with the limit, write bytes, then index the key. `EntryReservation` decrements pending on drop. Reads optionally decompress based on key metadata. `list` sorts indexed keys by modified time to support oldest-first replay. `delete` removes the directory and clears state.

Dependencies and integration points: depends on `rustfs_config` defaults/env (`ENV_TARGET_STORE_COMPRESS`), serde JSON, `snap`, UUIDs, tracing, and `StoreError`. Targets use it for durable at-least-once delivery queues.

Risks: `write_file` writes directly to the final path, so process crash during write can leave an empty/partial file that later reads as `NotFound` or deserialization failure. `put_multiple` stores concatenated JSON objects rather than a JSON array; `get_multiple` uses a stream deserializer and warns on partial batches, which is a fragile format. `entries` is only in-memory and must be rebuilt with `open`; callers must open before use. Compression choice is encoded in keys, so wrong key parsing breaks reads.

Test signals: unit tests cover compression env defaults, key compression flag, key round trip, raw byte round trip with compression, store deletion, entry limit enforcement, and concurrent `put_raw` respecting the limit.
