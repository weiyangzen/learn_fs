# File Research: sources/os/linux/linux-stable/fs/pstore/platform.c

## Summary
Implements the generic pstore platform layer. It owns backend registration, compression/decompression, kmsg dump integration, optional console/ftrace/pmsg frontend registration, and periodic rescanning of backend records.

## Main Responsibilities
- Register exactly one active `struct pstore_info` backend.
- Save kmsg dumps into backend records during panic/oops/emergency paths.
- Optionally compress dmesg records with zlib deflate.
- Decompress compressed dmesg records when reading from a backend.
- Register console, ftrace, pmsg, and kmsg-dumper frontends according to backend flags.
- Populate pstorefs from backend records and periodically rescan after survivable oopses.
- Manage the `backend`, `compress`, `kmsg_bytes`, and `update_ms` module parameters.

## Key Interfaces
- `pstore_register()` validates and activates a backend.
- `pstore_unregister()` unregisters all frontends, removes files, and clears global backend state.
- `pstore_record_init()` initializes record metadata and timestamp.
- `pstore_get_backend_records()` reads all records from a backend and creates pstorefs files.
- `pstore_type_to_name()` and `pstore_name_to_type()` translate record types.
- `pstore_dump()` is the `kmsg_dumper` callback.

## Important Behavior
`pstore_dump()` snapshots up to `kmsg_bytes` from the end of the kernel log. It avoids blocking in NMI, panic, and emergency paths by using `raw_spin_trylock_irqsave()` where needed. It writes a textual header, optionally compresses the combined header and log data, then calls the backend `write()` for each part.

Compression uses zlib deflate only. Unsupported `compress=` values are logged and treated as `deflate`; `compress=none` disables compression. If compression expands or fails, the code stores as much uncompressed data as fits.

`pstore_register()` validates backend flags and required `read`/`write` callbacks, installs a compatibility `write_user` wrapper when missing, initializes locks, loads existing records, and then registers enabled frontends. `pstore_unregister()` performs the inverse order and flushes timers/work before removing backend records.

`pstore_get_backend_records()` caps backend iteration at 65,536 records to prevent infinite loops, lets backend `read()` allocate record buffers, decompresses dmesg when needed, and transfers ownership to `pstore_mkfile()` on success.

## State and Synchronization
`psinfo_lock` protects global backend registration/unregistration and frontend setup. `psinfo->buf_lock` serializes crash-dump writes. `psinfo->read_mutex` serializes backend read/erase/open/close operations. A timer and work item handle delayed rescans when runtime updates are enabled.

## Cross-File Interactions
`inode.c` provides pstorefs file creation/removal. `ftrace.c` and `pmsg.c` register optional frontends. Backends in `ram.c` and `zone.c` provide `struct pstore_info` implementations.

## Risks
Pstore runs in crash paths, so backend write callbacks must be safe for the reasons they advertise. Compression allocation only happens at registration time, but compression work during dump still consumes CPU in sensitive paths. Only one backend is active globally.
