# File Research: sources/os/linux/linux/fs/pstore/platform.c

## Role

Core pstore platform/backend coordination layer. It owns single-backend registration, kmsg dump capture, optional compression, console/ftrace/pmsg frontend registration, record discovery, and backend unregister cleanup.

## Backend Registration

- `pstore_register()` enforces a single active backend, honors `backend=` selection, validates flags and required `read`/`write`, initializes locks, installs compatibility `write_user` if missing, loads existing records, and registers enabled frontends.
- `pstore_unregister()` unregisters pmsg/ftrace/console/kmsg callbacks, stops timer/work, removes backend files, frees compression buffers, clears `psinfo`, and releases the backend name.
- `pstore_record_init()` zeroes a record, attaches backend pointer, and timestamps it with `ktime_get_real_fast_ns()`.

## Kmsg Dump Capture

- `pstore_dump()` is registered as a `kmsg_dumper`.
- It snapshots up to `kmsg_bytes`, writing one or more `PSTORE_TYPE_DMESG` records with reason/count/part metadata.
- Panic/NMI/emergency paths use try-lock behavior to avoid blocking.
- Only the first backend write error is reported.
- Oops records can schedule delayed filesystem refresh through `pstore_update_ms`.

## Compression

- Supports only zlib deflate or `none`.
- Compression is only for dmesg records.
- `allocate_buf_for_compression()` allocates a worst-case compression buffer and zlib workspace.
- Failed or expanding compression falls back to uncompressed data truncated to backend buffer size.
- `decompress_record()` inflates compressed dmesg records before exposing them through pstorefs, preserving ECC notices.

## Frontends

- Kmsg dump frontend registers through `kmsg_dump_register()`.
- Console frontend writes `PSTORE_TYPE_CONSOLE` records from console callbacks.
- Ftrace and pmsg registration is delegated to optional frontend files.

## Record Discovery

- `pstore_get_backend_records()` opens the backend if needed, repeatedly calls backend `read()`, decompresses records, creates pstorefs files, detects loops with a 65536-record cap, and closes the backend.
- Uses `psi->read_mutex` to serialize backend reads and erase operations.

## Research Notes

This is the subsystem hub. It avoids complex dependencies in crash paths, limits compression choices to zlib/none, and centralizes frontend/backend lifetime ordering.
