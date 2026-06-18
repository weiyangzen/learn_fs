# sources/storage-engines/sqlite/src/printf.c

## Purpose
`printf.c` implements SQLite's locale-independent printf engine, dynamic string accumulator API, logging formatter, error-offset helpers, and reference-counted string allocation helpers. It replaces libc formatting for SQLite-owned code so output is deterministic across locales, bounded by SQLite limits, aware of SQLite memory allocators, and extended with SQLite-specific conversions for SQL quoting, JSON strings, parser tokens, source items, and dynamic string ownership.

The central formatter is `sqlite3_str_vappendf()`, which appends formatted output to a `sqlite3_str`/`StrAccum`. Public wrappers expose `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, `sqlite3_vsnprintf()`, `sqlite3_str_appendf()`, and internal `sqlite3MPrintf()`/`sqlite3VMPrintf()`.

## Important APIs, Types, and Functions
The format-dispatch table `fmtinfo[]` maps conversion characters to conversion classes such as decimal/radix integers, floating point, strings, dynamic strings, SQL quoting, JSON escaping, `%T` tokens, `%S` source items, `%p` pointers, `%r` ordinals, `%n`, and `%%`. Internal-only conversions are guarded by `SQLITE_PRINTF_INTERNAL`; public `sqlite3_mprintf()` cannot use parser-token or source-item conversions.

`sqlite3_str_vappendf(sqlite3_str*, const char*, va_list)` parses flags, width, precision, length modifiers, and conversion types. SQLite extensions include `%q` and `%Q` for SQL string escaping, `%w` for identifier-style double-quote escaping, `%j` and `%J` for JSON string literal escaping, `%z` for SQLite-owned dynamic strings, `%T`/`%#T` for tokens/expressions, `%S`/`%!S` for `SrcItem`, `%r` for English ordinals, `,` for thousands separators, and `!` for UTF-8 character-aware width/precision or alternate floating precision.

`StrAccum` management functions include `sqlite3StrAccumSetError()`, `sqlite3StrAccumEnlarge()`, `sqlite3StrAccumEnlargeIfNeeded()`, `sqlite3_str_appendchar()`, `sqlite3_str_append()`, `sqlite3_str_appendall()`, `sqlite3StrAccumFinish()`, `sqlite3ResultStrAccum()`, `sqlite3_str_finish()`, `sqlite3_str_errcode()`, `sqlite3_str_length()`, `sqlite3_str_truncate()`, `sqlite3_str_value()`, `sqlite3_str_reset()`, `sqlite3_str_free()`, `sqlite3StrAccumInit()`, and `sqlite3_str_new()`.

Error-offset helpers `sqlite3RecordErrorByteOffset()` and `sqlite3RecordErrorOffsetOfExpr()` record parser byte offsets for diagnostics when `%T`/`%#T` render tokens or expressions. `sqlite3_log()` formats bounded log messages via `renderLogMsg()`. `sqlite3DebugPrintf()` is available for debug/OS trace builds. `sqlite3RCStrRef()`, `sqlite3RCStrUnref()`, `sqlite3RCStrNew()`, and `sqlite3RCStrResize()` implement reference-counted strings/blobs.

## Control Flow
`sqlite3_str_vappendf()` scans literal text until `%`, appends literals directly, then parses flags (`-`, `+`, space, `#`, `!`, `0`, `,`), width (numeric or `*`), precision, and `l`/`ll`. It looks up the conversion type through an ASCII hash table or linear EBCDIC scan, then dispatches by conversion class.

Integer formatting fetches signed or unsigned values from either varargs or `PrintfArguments`, handles negative `SMALLEST_INT64` without overflow by two's-complement inversion, applies precision/zero padding, optional thousands separators, sign/prefix, radix conversion, and ordinal suffixes. Pointer formatting selects the length modifier based on pointer size and can be masked by trace flags.

Floating formatting decodes doubles through `sqlite3FpDecode()`, handles NaN/Inf specially, chooses fixed versus exponential for `%g/%G`, renders directly into the accumulator when possible, applies optional decimal points and trailing-zero trimming, and pads according to width and zero-fill rules. The formatter enforces `SQLITE_FP_PRECISION_LIMIT` and may allocate temporary buffers only when accumulator capacity cannot hold direct output.

String formatting handles `%s`, `%z`, and `%c`. `%z` either adopts the input allocation as the accumulator buffer for the special empty-output case or arranges to free it after appending. The `!` flag makes precision and width count UTF-8 characters rather than bytes. `%c` can duplicate the character according to precision using repeated doubling into the accumulator.

Escaping conversions append SQL, identifier, JSON, or `unistr()`-style escaped output. `%Q` wraps non-null strings in quotes and renders null pointers as SQL `NULL`; `%q` does not quote and renders null as `(NULL)`; `%w` doubles double quotes; `%j/%J` escape JSON control characters, quotes, and backslashes, with `%J` adding quotes or `null`. Alternate `#` on `%q/%Q` adds backslash control-character escaping, and `!` makes precision character-aware.

After each conversion, common width adjustment appends left/right padding and frees any temporary allocation. Accumulator growth is centralized in `sqlite3StrAccumEnlarge()`, which enforces maximum allocation, uses exponential growth where safe, copies static-base buffers into heap buffers, and sets `SQLITE_TOOBIG` or `SQLITE_NOMEM` error state on failure.

## State and Persistence Behavior
The formatter itself has no durable persistence, but it manages memory ownership across SQLite allocators. `StrAccum` can write into caller-provided fixed buffers (`mxAlloc==0`), database-aware allocations using `sqlite3DbRealloc()`, or global allocations using `sqlite3Realloc()`. Error state is sticky: once `accError` is set, append operations stop or reset owned memory. `sqlite3StrAccumSetError(SQLITE_TOOBIG)` also reports the error to the parser when a database handle is present.

`sqlite3_str_new()` returns a heap `sqlite3_str` with a length limit from the database or `SQLITE_MAX_LENGTH`. If allocation fails, it returns the static singleton `sqlite3OomStr`, which always reports `SQLITE_NOMEM` and must not be freed like a normal object. `sqlite3_str_finish()` transfers the final string to the caller and frees the accumulator object; `sqlite3ResultStrAccum()` transfers malloced text to an SQL function result with `SQLITE_DYNAMIC`.

`sqlite3RecordErrorByteOffset()` stores `db->errByteOffset` only if no offset has already been recorded and the token pointer falls within the current parse text. `sqlite3RecordErrorOffsetOfExpr()` walks through ON-clause wrapper expressions to find a usable expression offset and skips DDL-origin expressions. These offsets persist on the connection until the next error-state reset.

Reference-counted strings store an `RCStr` header immediately before the returned char pointer. `sqlite3RCStrRef()` increments, `sqlite3RCStrUnref()` decrements and frees at zero, and `sqlite3RCStrResize()` requires unique ownership (`nRCRef==1`) and frees on realloc failure.

## Dependencies and Integration Points
The file depends on `sqliteInt.h` for SQLite memory APIs, limits, parser and expression structures, UTF-8 helpers, floating decode helpers, result APIs, global configuration, logging callbacks, and compile-time feature flags. It is used pervasively by SQL construction, parser diagnostics, error messages, VDBE/debug tracing, JSON/SQL literal rendering, pragmas, schema loading, and any component using `sqlite3MPrintf()` or `sqlite3_str`.

Public API wrappers initialize SQLite automatically when autoinit is enabled. Internal wrappers use the database limit `SQLITE_LIMIT_LENGTH` and set OOM state on the database. `renderLogMsg()` intentionally uses a fixed stack buffer and `mxAlloc==0` because logging may happen while allocator mutexes are held.

The SQL function form uses `SQLITE_PRINTF_SQLFUNC` and `PrintfArguments` to fetch values from `sqlite3_value` arrays rather than varargs. This makes the same formatting engine available to SQL-level formatting while preserving type conversion semantics.

## Risks and Edge Cases
The highest-risk areas are allocation limits, ownership, and precision/width arithmetic. The code must avoid integer overflow while computing buffer sizes, enforce `SQLITE_PRINTF_PRECISION_LIMIT`/`SQLITE_FP_PRECISION_LIMIT`, and avoid large allocations from untrusted SQL formatting. `printfTempBuf()` checks requested temporary size against accumulator limits before allocation.

`%z` ownership is subtle: the input must be freed exactly once unless it is adopted as the accumulator buffer. Callers must only pass SQLite-allocated strings. `sqlite3_str_reset()` frees only buffers marked `SQLITE_PRINTF_MALLOCED`, so incorrect flag transitions can leak or double-free.

UTF-8 character-aware width and precision rely on byte scanning and continuation-byte counting, not full Unicode validation. Invalid UTF-8 can produce surprising widths but should not overrun buffers. `%c` with large precision uses repeated self-append; it relies on accumulator growth checks to prevent runaway memory.

Floating-point output has special behavior for NaN/Inf and alternate flags, including rendering NaN as `null` when zero-padded and substituting a large numeric representation for Inf under zero padding. Tests must preserve these SQLite-specific semantics. `sqlite3_log()` cannot safely use formats that allocate temporary memory while the allocator mutex is held.

Parser diagnostic integrations are pointer-sensitive. `%T` records offsets only when token pointers still refer into the current parse input. `%#T` skips expressions marked from DDL. Misuse outside active parse contexts should be harmless but will not produce useful offsets.

## Test Signals
Formatter tests should cover all public and internal conversion types, flags, width/precision combinations, `*` width/precision, `l`/`ll`, `SMALLEST_INT64`, alternate integer prefixes, thousands separators, pointer formatting, ordinal suffixes, NaN/Inf, `%g` fixed/exponential switching, locale independence of decimal points, and precision-limit clipping.

Escaping tests should cover null inputs, embedded quotes, backslashes, control characters, UTF-8 with `!`, precision truncation at character boundaries, `%#q/%#Q` `unistr()` output, JSON control escapes, `%J` null versus quoted string, and width padding after escaped output.

Accumulator tests should exercise fixed buffers (`sqlite3_snprintf()` truncation), dynamic growth, `SQLITE_TOOBIG`, OOM paths, adoption/freeing of `%z`, `sqlite3_str_truncate()`, `sqlite3_str_value()` on empty and non-empty strings, `sqlite3OomStr`, `sqlite3ResultStrAccum()` ownership transfer, and RC string ref/unref/resize behavior.
