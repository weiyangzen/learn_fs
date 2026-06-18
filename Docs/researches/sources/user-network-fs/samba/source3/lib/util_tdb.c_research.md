# sources/user-network-fs/samba/source3/lib/util_tdb.c

## Purpose
`util_tdb.c` contains source3 convenience routines around TDB packing, unpacking, logging, data rendering, and chain locking with alarm-based timeouts.

## Important APIs and Functions
The packing API is `tdb_pack` and `tdb_unpack`, with format specifiers for 8-bit, 16-bit, 32-bit, 64-bit, pointer-present tokens, null-terminated strings, fstrings, and length-prefixed blobs. `tdb_open_log` wraps `tdb_open_ex` with Samba DEBUG logging and loadparm-driven mmap/hash-size decisions. `tdb_data_cmp`, `tdb_data_string`, and `tdb_data_dbg` compare and render `TDB_DATA`. Lock helpers are `tdb_chainlock_with_timeout`, `tdb_lock_bystring_with_timeout`, and `tdb_read_lock_bystring_with_timeout`.

## Control Flow and Behavior
`tdb_pack_va` walks the format string, computes the write length even when no buffer is supplied, and writes little-endian values when space is available. `tdb_unpack` performs bounds checks before each decode and returns the consumed byte count or `-1`. For fixed blobs it checks integer wrap before allocation. `tdb_open_log` honors `lp_use_mmap`, derives per-database hash size from `tdb_hashsize:<basename>`, and supplies a logging callback. Chain-lock timeouts install a SIGALRM handler, register the alarm flag with TDB, perform read or write chain lock, then clear the alarm and handler.

## State and Persistence
TDB files opened by `tdb_open_log` are durable database state. Packing formats define persistent on-disk encoding for source3 TDB consumers. The lock timeout path uses process-global signal state (`gotalarm`, SIGALRM handler, process alarm), which is transient but process-wide.

## Dependencies and Integration Points
It depends on TDB, Samba loadparm, DEBUG, `cbuf`, hex encoding, signal helpers, and byte-order macros. It is integrated by many source3 databases that need compact records, debug rendering, and bounded lock waits.

## Risks and Edge Cases
The varargs packing contract is strict: wrong argument types or null strings for `P`/`f` can crash or panic. `tdb_pack_va` writes an 8-bit value with `SSVAL`, which writes two bytes, although the length is one; this is legacy behavior worth preserving carefully. Signal-based timeouts can interfere with other SIGALRM users in the same process. `tdb_log` leaks no memory on normal paths, but if `vasprintf` succeeds with an empty string it returns without freeing `ptr`. Lock debug prints `key.dptr` as a string, which is unsafe for non-string keys in diagnostics.

## Test Signals
Useful tests include pack-size-only calls, round-trip for every format specifier, truncated unpack inputs, oversized blob lengths and wrap checks, `tdb_open_log` hash-size/mmap configuration, `tdb_data_cmp` null and prefix cases, and chain lock timeout behavior under contention.
