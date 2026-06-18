# sources/storage-engines/sqlite/ext/qrf/qrf.c

## Purpose

`qrf.c` implements SQLite's Query Result Format utility library. Its public job is to run an already-prepared `sqlite3_stmt` and render its result rows in shell-style output formats such as box, table, markdown, CSV, JSON, SQL insert statements, line mode, list mode, EXPLAIN, EXPLAIN QUERY PLAN, and scanstatus/stat modes. It is designed as a reusable formatter behind `sqlite3_format_query_result()` rather than as a standalone extension entry point.

The implementation is stateful for the lifetime of a single formatting call. It consumes the caller's statement, optionally changes explain mode through `sqlite3_stmt_explain()`, steps the statement to completion or an error, writes formatted output through a `sqlite3_str` buffer and/or caller-supplied writer callback, resets the statement, restores explain mode, and releases all temporary allocations.

## Important APIs, Types, And Functions

The exported API implemented here is `sqlite3_format_query_result(sqlite3_stmt *pStmt, const sqlite3_qrf_spec *pSpec, char **pzErr)`. It returns an SQLite result code, treats `NULL` statements as no-ops, rejects a `NULL` spec with `SQLITE_MISUSE`, and rejects a busy statement with `SQLITE_BUSY`.

`Qrf` is the central private state object. It stores the statement and database handle, the accumulated `sqlite3_str` output, copied and normalized `sqlite3_qrf_spec`, row/column counts, current error state, output width/height limits, optional JSONB translation statement, and a union of mode-specific state for line mode, EQP graphing, EXPLAIN indentation, and multi-row INSERT accumulation.

`qrfInitialize()` copies the caller spec, validates `iVersion`, normalizes out-of-range enum values to auto, chooses defaults, configures style-specific text/blob/null/title behavior, and switches statements into EXPLAIN or EXPLAIN QUERY PLAN mode when needed. `qrfFinalize()` emits style-specific trailers, flushes output, transfers `pzOutput` ownership if requested, frees mode-specific allocations, restores any prior explain mode, finalizes JSONB helper state, and propagates `sqlite3_str` errors.

Rendering helpers include `qrfRenderValue()` for SQLite value-to-text/blob conversion, `qrfEncodeText()` for SQL/CSV/HTML/Tcl/JSON/plain/relaxed text quoting, `qrfEscape()` for control-character escaping, `qrfDisplayWidth()`, `sqlite3_qrf_wcwidth()`, `sqlite3_qrf_wcswidth()`, `sqlite3_qrf_decode_utf8()`, and `qrfIsVt100()` for terminal-display width accounting. The width logic accounts for tabs, newlines, VT100 escapes, zero-width Unicode, and double-width Unicode through the large `aQrfUWidth` span table.

Columnar formatting is organized through `qrfColData`, `qrfColumnar()`, `qrfWrapLine()`, `qrfWidthPrint()`, `qrfPrintAligned()`, `qrfRowSeparator()`, `qrfBoxSeparator()`, `qrfSplitColumn()`, and `qrfRestrictScreenWidth()`. EXPLAIN and planner output use `qrfExplain()`, `qrfScanStatusVm()`, `qrfEqpAppend()`, `qrfEqpRender()`, `qrfEqpRenderLevel()`, and, when `SQLITE_ENABLE_STMT_SCANSTATUS` is available, `qrfEqpStats()` and `qrfStatsHeight()`.

## Control Flow

`sqlite3_format_query_result()` initializes `Qrf`, dispatches by normalized style, resets the statement, finalizes the formatter, and returns `qrf.iErr`. Box, column, markdown, and table styles call `qrfColumnar()` because they need all rows materialized to compute widths before printing. Explain style calls `qrfExplain()`. Stats VM builds a temporary `bytecode(?1)` query and routes it through EXPLAIN formatting. Stats and StatsEst synthesize EQP-like output from scanstatus. All other styles stream row-by-row through `qrfOneSimpleRow()`.

`qrfColumnar()` performs an initial `sqlite3_step()` to detect whether any rows exist. It then materializes optional headers and all cells into `qrfColData`, tracking natural display widths, numeric cells, multi-line cells, and maximum widths per column. After stepping is complete, it computes alignment, applies fixed or natural widths, enforces `nWrap`, optionally splits one-column output into multiple visual columns, optionally squashes wide columns to `nScreenWidth`, then renders headers/body/separators/borders. Multi-line cells are repeatedly passed through `qrfWrapLine()` until exhausted or `nLineLimit` is reached, in which case an ellipsis row is emitted.

`qrfOneSimpleRow()` handles streaming formats. JSON and JObject open or separate row objects and delegate to `qrfOneJsonRow()`. HTML emits table rows and optional header rows. INSERT mode batches rows into `INSERT INTO ... VALUES(...)` statements until `nMultiInsert` is reached, quoting identifiers conservatively with `qrf_need_quote()`. Line mode lazily caches column-name labels and prints each value under its label with optional wrapping. EQP mode accumulates graph rows and flushes when special separator rows are encountered. List-like modes optionally print titles, then render cells separated by `zColumnSep` and `zRowSep`.

`qrfExplain()` is explicitly two-pass. The first pass scans opcode rows and computes indentation based on loop and branch opcodes (`Next`, `Prev`, `VNext`, `VPrev`, `SorterNext`, `Return`, `Goto` with matching yield/seek/rewind targets). It resets the statement and performs a second pass to print a fixed-width table, with an alternate column map for scanstatus VM output. This assumes the first columns are equivalent to ordinary EXPLAIN output.

## State And Persistence Behavior

All durable state remains outside this file. The formatter does not write database tables or files itself; persistence is limited to the caller's statement state and caller-provided output target. It always calls `sqlite3_reset()` on the statement after dispatch and attempts to restore any prior explain mode recorded in `expMode`.

Output state is transient. `pOut` accumulates text until `qrfWrite()` flushes to `xWrite`, or until finalize transfers/finishes it. If `pSpec->pzOutput` is set, finalize either stores the finished string there or appends to an existing allocation using `sqlite3_realloc64()`. If `xWrite` is set, blobs in raw text mode can be written directly after flushing pending buffered text.

Some temporary SQLite state is created. JSONB rendering may open an in-memory database and prepare `SELECT json(?1)` into `pJTrans`; it is finalized and the in-memory database is closed in `qrfFinalize()`. Stats VM prepares a temporary query over `bytecode(?1)` and binds the original statement pointer.

## Dependencies And Integration Points

The file depends on `qrf.h`, the SQLite C API, `sqlite3_str`, `sqlite3_stmt_explain()`, `sqlite3_stmt_isexplain()`, `sqlite3_column_*()`, `sqlite3_keyword_check()`, `sqlite3_malloc64()/realloc64()/free()`, and optional scanstatus APIs under `SQLITE_ENABLE_STMT_SCANSTATUS`. It assumes SQLite printf extensions such as `%Q`, `%#Q`, and `%w`.

The primary integration point is clients that prepare a statement and pass a `sqlite3_qrf_spec`. The spec can redirect output through `xWrite`, collect it through `pzOutput`, customize value rendering through `xRender`, specify separators/table names/null text, and tune width, wrapping, title, alignment, JSONB, and blob behavior. The EXPLAIN and scanstatus modes integrate with SQLite VM introspection and the optional `bytecode()` table-valued function.

## Risks And Edge Cases

Columnar modes materialize the complete result set in memory, so very large result sets can consume substantial memory before producing output. This is intentional for width computation but a different risk profile from streaming styles. Width and Unicode calculations are approximate by design; terminals can disagree on zero-width or double-width character display, causing misalignment.

`qrfRenderValue()` relies on the caller's `xRender` returning SQLite-allocated memory that can be released with `sqlite3_free()`. Raw BLOB text output assumes `xWrite` exists in the default BLOB-text path; otherwise a raw text BLOB with no writer would be unsafe if such a spec combination is constructed. JSONB detection is a fast sanity check with possible false positives, though the `json(?1)` step is the real converter. `qrfJsonbToJson()` opens an auxiliary in-memory connection, so builds without JSON support simply fail to translate and fall back to ordinary blob rendering.

The code modifies statement explain mode for Eqp and Explain and restores it in finalize, but errors during initialization still flow through finalize because the public entry point dispatches using normalized state. Statement reset errors after stepping are captured by `qrfResetStmt()` only if no earlier error exists. `qrfColumnar()` returns early for no rows without resetting itself; the public wrapper performs reset afterward.

## Test Signals

High-value tests should cover every style in `qrf.h`, especially Box/Table/Markdown/Column width calculation, one-column split layout, `nScreenWidth`, `nWrap`, `nLineLimit`, title truncation, right/center/vertical alignment, and fixed negative widths. Encoding tests should include SQL, relaxed SQL, CSV separator collisions, HTML metacharacters, JSON/Tcl control characters, alternate escape modes, NULL rendering, raw and quoted blobs, and optional JSONB-as-text behavior.

Planner formatting tests should cover ordinary `EXPLAIN`, `EXPLAIN QUERY PLAN`, statement mode restoration, Stats/StatsEst with and without `SQLITE_ENABLE_STMT_SCANSTATUS`, and StatsVm/`bytecode(?1)` output where available. Error-path tests should cover busy statements, bad `iVersion`, writer callback failure, renderer callback results, OOM injection, `sqlite3_reset()` errors, large output with `pzOutput` append, and display width behavior for tabs, VT100 sequences, invalid UTF-8-like bytes, and double-width Unicode.
