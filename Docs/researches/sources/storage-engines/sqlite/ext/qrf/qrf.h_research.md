# sources/storage-engines/sqlite/ext/qrf/qrf.h

## Purpose

`qrf.h` is the public interface for SQLite's Query Result Format utility library. It defines the user-facing format specification structure, the single formatter entry point, constants for all supported output styles and encoding policies, tri-state switches, alignment values, and display-width helper declarations. The header is intentionally small and C/C++ compatible so callers can embed the formatter without depending on private implementation details from `qrf.c`.

## Important APIs, Types, And Constants

The central public type is `sqlite3_qrf_spec`. It is a versioned options structure. Its leading fields select style and encoding behavior: `iVersion`, `eStyle`, `eEsc`, `eText`, `eTitle`, and `eBlob`. Boolean-like fields are tri-state switches using `QRF_SW_Auto`, `QRF_SW_Off`, and `QRF_SW_On`: `bTitles`, `bWordWrap`, `bTextJsonb`, `bSplitColumn`, and `bBorder`.

Layout fields include `eDfltAlign`, `eTitleAlign`, `nWrap`, `nScreenWidth`, `nLineLimit`, `nTitleLimit`, `nCharLimit`, per-column width and alignment counts (`nWidth`, `nAlign`), and arrays (`aWidth`, `aAlign`). Text output customization includes `zColumnSep`, `zRowSep`, `zTableName`, and `zNull`. Extensibility hooks include `xRender` for caller-provided value rendering, `xWrite` for streaming output, `pRenderArg`, `pWriteArg`, and `pzOutput` for returning an allocated output string.

The primary function is `sqlite3_format_query_result(sqlite3_stmt *pStmt, const sqlite3_qrf_spec *pSpec, char **pzErr)`. The caller prepares a statement, fills a spec, and receives either formatted output through the spec's writer/string fields or an error code plus optional message.

Style constants range from automatic choice through table-like, delimiter, structured, planner, and suppress/count modes: `QRF_STYLE_Auto`, `Box`, `Column`, `Count`, `Csv`, `Eqp`, `Explain`, `Html`, `Insert`, `Json`, `JObject`, `Line`, `List`, `Markdown`, `Off`, `Quote`, `Stats`, `StatsEst`, `StatsVm`, and `Table`.

Text constants control text quoting: auto, plain, SQL, CSV, HTML, Tcl, JSON, and relaxed SQL. Blob constants control whether BLOB values are shown as raw text, SQL literal, hex, Tcl string, JSON string, size-only marker, or chosen automatically from text style. Escape constants control whether control characters are left alone, escaped as ASCII caret notation, or escaped as Unicode control pictures.

Alignment constants combine horizontal and vertical bits. `QRF_ALIGN_HMASK` selects left/center/right/auto and `QRF_ALIGN_VMASK` selects top/middle/bottom/auto; compound constants such as `QRF_ALIGN_NW`, `QRF_ALIGN_C`, and `QRF_ALIGN_SE` encode both axes.

The header also declares `sqlite3_qrf_wcwidth(int c)` and `sqlite3_qrf_wcswidth(const char*)` for estimating terminal display width.

## Control Flow Expectations

The header does not implement behavior, but it defines the contract followed by `qrf.c`. Callers provide an idle prepared statement and a spec. The implementation may consume all rows, reset the statement, and, for explain-related styles, temporarily switch statement explain mode. Columnar styles generally require complete result materialization to compute widths; list-like, JSON, HTML, insert, line, count, off, and EQP styles can stream row-by-row internally.

Defaults are mostly selected by the implementation when fields are zero or `QRF_*_Auto`. For example, automatic style chooses a normal table style for ordinary statements and planner-oriented styles for explain statements. Automatic title, text, blob, separator, null, and wrapping behavior is style-sensitive.

## State And Persistence Behavior

`sqlite3_qrf_spec` is passed by pointer but copied by the implementation before normalization. The strings and arrays referenced by the spec are caller-owned for the duration of the call. `pzOutput`, when non-NULL, is an output ownership channel: the formatter stores or extends a SQLite-allocated string and the caller is expected to release it with `sqlite3_free()`. `xRender` must return a SQLite-allocated string because the implementation releases it with `sqlite3_free()`.

No persistent database state is described by this header. The API formats query results and may use SQLite statement/database metadata, but durable writes are only whatever the caller's original statement performs while being stepped.

## Dependencies And Integration Points

The header depends on `sqlite3.h` and standard `stdlib.h`. It wraps declarations in `extern "C"` for C++ consumers. Integration is through the SQLite C API: callers pass `sqlite3_stmt*`, receive SQLite result codes, and use SQLite memory allocation conventions for returned strings and callbacks.

The spec is deliberately versioned with `iVersion` and a future-extension comment at the end of the struct. This means callers should initialize the structure predictably, normally with zero-filled storage plus explicit fields, so new trailing fields can default to automatic behavior.

## Risks And Edge Cases

Because this is a public ABI-style structure, field ordering and size matter. The implementation currently accepts only supported `iVersion` values, so callers that set a future version against an older library receive an error. Uninitialized specs are risky: many zero values mean auto, but pointer fields and counts must still be coherent. `nWidth` and `nAlign` must not exceed the actual lengths of `aWidth` and `aAlign`; the implementation trusts those counts.

Width limits use narrow integer fields for some options (`short int` for wrap/screen/line/title limits) and `int` for character limits. Very high requested widths should respect `QRF_MAX_WIDTH`/`QRF_MIN_WIDTH` and implementation caps. Display width helpers are estimates, not Unicode-rendering guarantees.

The callback contracts are important. A writer callback returning non-zero becomes a formatter error. A render callback can override all built-in type rendering for a value; if it returns NULL the built-in rendering path is used.

## Test Signals

Tests for this header/API boundary should compile the header from C and C++, zero-initialize specs, use every enum family, pass custom `xWrite` and `xRender` callbacks, and verify `pzOutput` allocation/append semantics. ABI-oriented tests should confirm old-version specs are accepted and unsupported versions are rejected. API misuse tests should cover `NULL` specs, `NULL` statements, busy statements, inconsistent width/alignment counts, and caller strings/separators used by CSV/List/Line/Insert modes.
