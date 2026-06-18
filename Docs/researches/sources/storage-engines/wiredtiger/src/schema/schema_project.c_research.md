# sources/storage-engines/wiredtiger/src/schema/schema_project.c

Purpose: executes projection plans produced by schema planning code, moving packed key/value fields between application varargs, dependent cursors, raw value buffers, and merged output buffers.

Important APIs and functions: `__wt_schema_project_in` reads application varargs into the key/value buffers of dependent cursors. `__wt_schema_project_out` reads dependent cursor buffers back into application varargs. `__wt_schema_project_slice` projects from a raw packed value into cursor buffers, optionally key-only. `__wt_schema_project_merge` merges fields from dependent cursors into a single packed output buffer.

Control flow: all functions parse a compact plan string of cursor indices plus projection op characters. Key/value switch ops select the target cursor buffer and initialize the correct pack format, with record-number cursors using `"R"`. Skip ops advance or append default values for out-of-order insertion. Next ops consume a new application or raw value and write/read it once. Reuse ops read the same previously consumed value into another projected location without advancing the source varargs/value. Buffer edits preserve existing packed content by unpacking old fields, growing buffers, memmoving tail bytes, and rewriting fields in place.

State and persistence behavior: mutates `WT_CURSOR` key/value buffers and output `WT_ITEM` buffers only. It does not write metadata or storage directly, but its packed results are later used by cursor insert/update/search operations.

Dependencies and integration points: depends on projection plan strings from `schema_plan.c`, pack/unpack helpers, `WT_PACK_GET`/`WT_UNPACK_PUT` vararg macros, cursor key/value formats, record-number cursor conventions, and buffer growth utilities. Table, index, and column-group cursors use these helpers to expose logical table projections over physical stores.

Risks: plan parsing uses `strtoul` with embedded op chars, so malformed plans can desynchronize parsing. In-place packed-buffer edits are offset-sensitive and must preserve record-number key storage. Raw value projection must maintain compatible pack types between source and destination. Key-only slice mode must skip value writes without consuming the wrong plan state.

Test signals: projection round trips for multi-column tables, duplicate/reused columns, out-of-order inserts that append default values, record-number keys, raw `u`/`U` fields, key-only index extraction, merge/slice compatibility, and malformed plan assertions in diagnostic builds.
