# sources/object-store/openstack-swift/swift/cli/recon_cron.py

Purpose: periodic object-server cron helper that counts async pending update files and writes recon cache values consumed by recon middleware and `swift-recon`.

Important APIs: `get_async_count(device_dir)` and `main()`.

Control flow: `main()` requires an object-server config path, reads the `filter:recon` section, derives device directory, recon cache path, and lock path, then takes a lock named `swift-recon-object-cron`. Under the lock it calls `get_async_count()`, which walks devices and counts entries in `async_pending` or policy-specific `async_pending-*` hash directories. It dumps `async_pending` and `async_pending_last` to the object recon cache file.

State and persistence: reads device directories and writes a recon cache JSON file. Locking prevents overlapping cron instances.

Dependencies and integration: uses `readconf`, `lock_path`, `listdir`, `dump_recon_cache`, `RECON_OBJECT_FILE`, and `ASYNCDIR_BASE`. Its output feeds recon middleware `/recon/async`.

Risks: directory walk cost scales with devices and pending hashes. Exceptions while accessing devices are logged and return error code 1. Tests should cover policy-specific async dirs, non-directory entries, locking, config defaults, recon cache payload, and exception handling.
