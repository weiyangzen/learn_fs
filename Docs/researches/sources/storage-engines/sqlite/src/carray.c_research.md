# sources/storage-engines/sqlite/src/carray.c

## Purpose

`carray.c` implements the optional `carray` eponymous virtual table/table-valued function, enabled only when virtual tables are present and `SQLITE_ENABLE_CARRAY` is defined. It exposes caller-supplied C arrays to SQL rows, supporting pointer/count/ctype hidden-column constraints and a newer `sqlite3_carray_bind[_v2]()` API for safer single-argument binding.

## Important APIs, Types, and Functions

- `carray_bind` stores bound array metadata: data pointer, element count, type flags, destructor, and destructor argument.
- `carray_cursor` tracks scan state: current one-based rowid, array pointer, count, and element type.
- `carrayConnect()` declares `CREATE TABLE x(value,pointer hidden,count hidden,ctype hidden)`.
- `carrayBestIndex()` chooses among empty scan, single `pointer` bind (`idxNum=1`), pointer+count (`idxNum=2`), and pointer+count+ctype (`idxNum=3`).
- `carrayFilter()` decodes bound parameters into cursor state using pointer types `"carray-bind"` or `"carray"`.
- `carrayColumn()` materializes values as integer, int64, double, text, or blob from `struct iovec`.
- `sqlite3_carray_bind_v2()` and `sqlite3_carray_bind()` bind a `carray_bind` object to a statement parameter.
- `sqlite3CarrayRegister()` registers the module as `"carray"`.

## Control Flow and Behavior

The planner requests constraints on hidden columns. If only `pointer=` is usable, the value must be a pointer bound by `sqlite3_carray_bind_v2()` with type `"carray-bind"`, and count/type come from `carray_bind`. If `pointer=` and `count=` are usable, the pointer must be bound with pointer type `"carray"` and the type defaults to `int32`. A usable `ctype=` switches to typed values after validating against `azCarrayType`.

The cursor starts at rowid 1 and advances by incrementing `iRowid`. EOF occurs when `iRowid > iCnt`. `value` reads `pPtr[iRowid-1]` according to `eType`; hidden columns either return count/type or no pointer value. Invalid or unconstrained inputs yield an empty table instead of dereferencing.

Binding with `SQLITE_TRANSIENT` copies the array into one allocation. Text arrays copy the pointer array plus nul-terminated strings; blob arrays copy `struct iovec` entries plus blob payloads; numeric arrays copy fixed-width bytes. Non-transient binding stores the supplied pointer and destructor metadata. The bound object is attached with `sqlite3_bind_pointer()` and cleaned up by `carrayBindDel()`.

## State and Persistence

The virtual table is stateless except for per-cursor scan state and per-parameter `carray_bind` objects owned by prepared statements. It does not write database storage. Destructor handling is the main state lifecycle: `SQLITE_STATIC` means no caller destructor, `SQLITE_TRANSIENT` means SQLite owns copied memory, and other callbacks are invoked for `pDestroy` or `aData` depending on the API variant.

## Dependencies and Integration Points

This file depends on the virtual table API, pointer binding API, result APIs, SQLite memory allocation, and `struct iovec` availability. On Windows-like targets it defines a local `struct iovec`. SQL integration is via `sqlite3VtabCreateModule()`, allowing `SELECT * FROM carray(...)` syntax through eponymous virtual tables.

## Risks and Edge Cases

The legacy pointer/count form can dereference invalid C pointers if callers bind wrong addresses or lifetimes. `carrayBestIndex()` rejects partial multi-argument usage where `count` or `ctype` constraints are present but unavailable, preventing silently wrong function-call semantics. `sqlite3_carray_bind_v2()` validates `mFlags`, but it does not guard negative `nData` beyond normal size arithmetic expectations; callers must pass sane counts. Large transient text/blob arrays can overflow or OOM if size accumulation exceeds allocator limits. Blob `iov_len` is cast to `int` in `sqlite3_result_blob()`, so extremely large individual blobs are outside practical safe use.

## Test Signals

Tests should cover all five element types, null text entries, transient copy lifetime after caller memory is freed, custom destructors and `pDestroy`, unknown `ctype` error reporting, unconstrained empty scans, partial hidden-column constraint rejection, pointer type mismatches, planner estimates and `omit` flags, and registration when `SQLITE_ENABLE_CARRAY` is disabled.
