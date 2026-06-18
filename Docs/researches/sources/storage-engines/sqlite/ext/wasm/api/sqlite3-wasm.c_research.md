# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-wasm.c

## Purpose
This C file is the wasm-specific SQLite compilation unit. It sets SQLite build defaults for wasm, includes the SQLite amalgamation directly so wasm helpers can access private state, and exports internal helper functions used by the JavaScript bindings. The exported helpers are not public SQLite APIs; they bridge wasm memory management, enum/struct metadata, VFS file operations, serialization/import/export helpers, kvvfs internals, variadic config wrappers, optional WASMFS OPFS initialization, and C-side test hooks.

## Important APIs, Types, and Functions
Build configuration defines `SQLITE_WASM`, hardens or adjusts defaults such as `SQLITE_ENABLE_API_ARMOR`, `SQLITE_THREADSAFE=0`, `SQLITE_TEMP_STORE=2`, URI support, default page/cache sizes, disabled deprecated/load-extension/shared-cache/UTF16 features, optional bare-bones feature removal, and optional `SQLITE_EXTRA_INIT_MUTEXED`. It defines `SQLITE_WASM_EXPORT`, `SQLITE_WASM_EXPORT_NAMED`, and `SQLITE_WASM_EXPORT2` for explicit wasm exports.

The pseudo-stack API includes `sqlite3__wasm_pstack_ptr()`, `sqlite3__wasm_pstack_restore()`, `sqlite3__wasm_pstack_alloc()`, `sqlite3__wasm_pstack_remaining()`, and `sqlite3__wasm_pstack_quota()`, backed by a static 4 KiB aligned buffer. `sqlite3__wasm_enum_json()` emits JSON for constants and struct layouts, including result codes, open flags, config values, VFS/io/file structs, kvvfs structs, and virtual table structs when enabled.

Operational wrappers include `sqlite3__wasm_vfs_unlink()`, `sqlite3__wasm_db_vfs()`, `sqlite3__wasm_db_reset()`, `sqlite3__wasm_db_export_chunked()`, `sqlite3__wasm_db_serialize()`, `sqlite3__wasm_vfs_create_file()`, `sqlite3__wasm_posix_create_file()`, `sqlite3__wasm_kvvfsMakeKey()`, `sqlite3__wasm_kvvfs_methods()`, `sqlite3__wasm_vtab_config()`, `sqlite3__wasm_db_config_ip()`, `sqlite3__wasm_db_config_pii()`, `sqlite3__wasm_db_config_s()`, `sqlite3__wasm_config_i()`, `sqlite3__wasm_config_ii()`, `sqlite3__wasm_config_j()`, `sqlite3__wasm_qfmt_token()`, `sqlite3__wasm_kvvfs_decode()`, `sqlite3__wasm_kvvfs_encode()`, and `sqlite3__wasm_init_wasmfs()`.

When `SQLITE_WASM_ENABLE_C_TESTS` is enabled, additional exported probes exercise struct binding, pointer, int64, stack overflow, string deallocation, and SQLTester glob behavior.

## Control Flow
Compilation first applies wasm-specific SQLite options, optionally strips features for bare-bones builds, includes `sqlite3.c`, then defines helper exports. The pseudo-stack is a downward-growing stack: callers save the current pointer, allocate zeroed aligned blocks, and restore to a saved pointer. `sqlite3__wasm_enum_json()` lazily fills a static JSON buffer. It leaves byte 0 empty until the end to reduce a small race where a concurrent caller could observe a partially generated buffer.

Database file helpers use core SQLite or VFS methods. `sqlite3__wasm_db_export_chunked()` obtains the main database file pointer via `SQLITE_FCNTL_FILE_POINTER`, chooses a chunk size aligned to the database size when possible, reads through `xRead`, and invokes a callback for each chunk. `sqlite3__wasm_db_serialize()` wraps `sqlite3_serialize()` and returns `SQLITE_NOMEM` only when no output pointer is produced and `SQLITE_SERIALIZE_NOCOPY` was not requested. `sqlite3__wasm_vfs_create_file()` opens a VFS file, optionally locks it, truncates, writes in 512-byte blocks, unlocks/closes, and deletes newly created files on failure. The POSIX variant uses `fopen()`/`fwrite()` for Emscripten-style filesystems.

## State and Persistence Behavior
Static state includes the pseudo-stack buffer, the enum JSON buffer, static kvvfs key buffer, and the optional singleton WASMFS OPFS backend. `sqlite3__wasm_db_reset()` changes a database by enabling reset-database mode and running `VACUUM`; it warns that virtual table `xDestroy()` is not called. VFS create/unlink helpers modify storage behind the selected VFS. WASMFS initialization creates and mounts an OPFS backend at a single-component mount point such as `/opfs` when compiled with Emscripten WASMFS support, otherwise returns `SQLITE_NOTFOUND`.

## Dependencies and Integration Points
This file depends on SQLite internals from `sqlite3.c`, `os_kv.c` private kvvfs symbols, C99, wasm export attributes, optional Emscripten WASMFS headers, and build-time macros from the wasm build system. JavaScript bindings consume `sqlite3__wasm_enum_json()` to build constant maps and struct binders, use pseudo-stack functions for temporary output pointers, and call VFS/config/serialization wrappers to avoid unsupported variadic or private C interfaces in JS.

## Risks and Edge Cases
`sqlite3__wasm_enum_json()` has a fixed 20 KiB static buffer guarded by assertions and can return null if metadata grows too large. Memory64 builds are noted as problematic. The pseudo-stack is tiny and only for small temporaries; misuse of restore pointers is undefined outside assertions. `sqlite3__wasm_vfs_create_file()` is deprecated for generic VFS import because out-of-scope VFS use can trigger SQLite debug assertions. It also uses 32-bit `nData`, limiting large imports. Variadic config wrappers intentionally return `SQLITE_MISUSE` for unsupported op codes. The wasm build is single-threaded except where browser storage VFSes provide their own coordination.

## Test Signals
Test coverage should verify enum JSON parses and matches C struct sizes/offsets, pseudo-stack alignment/quota/restore behavior, serialization and chunked export results, VFS create/unlink behavior on default, OPFS, and unsupported VFSes, POSIX file creation, kvvfs encode/decode/key size behavior, db/vtab/config wrapper allowed and rejected op codes, WASMFS init return codes with and without support, and C-test exports when enabled. SQLTester glob tests should cover `*`, `?`, bracket ranges, inversion, and `#` numeric matching.
