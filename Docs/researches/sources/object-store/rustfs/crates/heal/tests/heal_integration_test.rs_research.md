# sources/object-store/rustfs/crates/heal/tests/heal_integration_test.rs

This serial integration suite exercises heal behavior against a real local four-disk ECStore. `setup_test_env` initializes tracing once, creates `/tmp/rustfs_heal_heal_test_<uuid>`, creates four disk dirs, assigns endpoint indexes, formats local disks, builds `ECStore` on `127.0.0.1:9001`, initializes bucket metadata, and wraps the store in `ECStoreHealStorage`. A `OnceLock` reuses this environment across serial tests.

Tests delete object shard `part.*` files, bucket directories, `format.json`, or an entire disk directory, then run object, bucket, and format heal paths. They verify restored files with polling and verify object data by reading through ECStore. The direct storage API test covers dry-run `heal_format`, `heal_bucket`, and `heal_object`.

Persistent state is real temporary filesystem data and ECStore metadata. Dependencies include ECStore operations, `HealManager`, `HealRequest`, `HealOpts`, `walkdir`, HTTP headers, Tokio FS/time, and `serial_test`. Risks are hard-coded port `9001`, filesystem timing, and shared test environment state; the value is high because it validates actual recovery of non-inline object data and format metadata.
