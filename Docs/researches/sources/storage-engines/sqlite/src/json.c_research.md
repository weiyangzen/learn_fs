# sources/storage-engines/sqlite/src/json.c

## Purpose

`json.c` implements SQLite's built-in JSON subsystem when `SQLITE_OMIT_JSON` is not defined. It provides scalar functions (`json`, `jsonb`, `json_array`, `json_extract`, `json_set`, `json_patch`, `json_valid`, `json_error_position`, etc.), aggregate/window functions (`json_group_array`, `json_group_object` and JSONB variants), the `->` and `->>` operators, and the `json_each`/`json_tree` plus `jsonb_each`/`jsonb_tree` table-valued functions.

The file's central design is to normalize inputs into SQLite's internal JSONB representation (`JsonParse.aBlob`) and then operate on that binary representation for lookup, mutation, rendering, validation, and traversal. Text JSON remains the public canonical output format for `json_*` functions, while `jsonb_*` functions return BLOB JSONB. JSON5-style input extensions are accepted and canonicalized to strict RFC-8259 JSON text on text output.

## Important APIs, Types, and Functions

- `JsonParse` owns or references parsed JSONB bytes, original text, parse/cache metadata, edit state (`eEdit`, `delta`, `aIns`, `nIns`, `iLabel`), error flags, depth, and DB allocator context.
- `JsonString` is the output accumulator used for JSON text and intermediate strings. It starts with static storage and grows into reference-counted strings.
- `JsonCache` stores up to four `JsonParse` entries in SQLite auxdata, keyed by JSON argument text, so repeated function calls within a statement can avoid reparsing.
- JSONB type codes `JSONB_NULL` through `JSONB_OBJECT` encode primitive, text, array, and object nodes. Payload sizes live in the high nibble or in 1/2/4/8-byte big-endian size fields.
- Parser and encoder functions include `jsonTranslateTextToBlob`, `jsonConvertTextToBlob`, `jsonArgIsJsonb`, `jsonFunctionArgToBlob`, `jsonBlobAppendNode`, `jsonbPayloadSize`, and `jsonbValidityCheck`.
- Renderer functions include `jsonTranslateBlobToText`, `jsonTranslateBlobToPrettyText`, `jsonReturnFromBlob`, `jsonReturnTextJsonFromBlob`, `jsonReturnParse`, and `jsonReturnString`.
- Path lookup and edit are centered on `jsonLookupStep`, supported by `jsonLabelCompare`, `jsonCreateEditSubstructure`, `jsonBlobEdit`, `jsonAfterEditSizeAdjust`, and `jsonInsertIntoBlob`.
- Scalar SQL entry points include `jsonQuoteFunc`, `jsonArrayFunc`, `jsonArrayLengthFunc`, `jsonExtractFunc`, `jsonPatchFunc`, `jsonObjectFunc`, `jsonRemoveFunc`, `jsonReplaceFunc`, `jsonSetFunc`, `jsonTypeFunc`, `jsonPrettyFunc`, `jsonValidFunc`, and `jsonErrorFunc`.
- Aggregate/window entry points are `jsonArrayStep`, `jsonArrayCompute`, `jsonArrayValue`, `jsonArrayFinal`, `jsonObjectStep`, `jsonObjectCompute`, `jsonObjectValue`, `jsonObjectFinal`, and optionally `jsonGroupInverse`.
- Virtual table support uses `JsonEachConnection`, `JsonEachCursor`, `JsonParent`, `jsonEachConnect`, `jsonEachBestIndex`, `jsonEachFilter`, `jsonEachNext`, `jsonEachColumn`, and `jsonEachModule`.
- Public registration is through `sqlite3RegisterJsonFunctions()` and, when virtual tables are enabled, `sqlite3JsonVtabRegister()`.

## Control Flow

For scalar functions, SQL arguments enter through function-specific wrappers. Most functions call `jsonParseFuncArg()` for the primary JSON input. That routine checks NULL handling, searches the auxdata cache for text inputs, recognizes JSONB BLOBs via `jsonArgIsJsonb()`, falls back to parsing text with `jsonConvertTextToBlob()`, and caches immutable parses. Editable operations request `JSON_EDITABLE`, causing cached parses to be copied into writable storage before mutation.

Text parsing is recursive descent in `jsonTranslateTextToBlob()`. It recognizes objects, arrays, strings, numbers, booleans, nulls, JSON5 whitespace/comments, single-quoted strings, identifier labels, hex numbers, `Infinity`, and `NaN` variants. The parser appends JSONB nodes into `aBlob`, backpatches array/object payload sizes after children are parsed, tracks non-standard JSON features in `hasNonstd`, and enforces `JSON_MAX_DEPTH`.

JSONB inputs take a faster path. `jsonArgIsJsonb()` verifies the outer element's type and size and performs full validation for small payloads that could be confused with text JSON cast to BLOB. Strict validation is delegated to `jsonbValidityCheck()`, which recursively checks type-specific payload syntax, object label/value pairing, and nesting limits.

Extraction and mutation use `jsonLookupStep()`. Path segments are parsed as object labels (`.name`, `."quoted"`) or array indexes (`[N]`, `[#]`, `[#-N]`). On exact matches the routine recurses into child nodes. With an edit mode set, it deletes, replaces, inserts, sets, or array-inserts in-place by calling `jsonBlobEdit()`. Missing paths for insert/set can synthesize intermediate object or array substructures through `jsonCreateEditSubstructure()`.

Rendering reverses JSONB into SQL results. Primitive nodes can return SQL NULL/integer/real/text from `jsonReturnFromBlob()`. Arrays and objects render to JSON text through `jsonTranslateBlobToText()` unless JSONB output is requested. `json_pretty` uses `JsonPretty` and `jsonTranslateBlobToPrettyText()` to add indentation. Generated text JSON is tagged with `JSON_SUBTYPE` where appropriate so nested JSON builders know when text arguments are already JSON.

`json_patch` implements RFC-7396 merge patch in `jsonMergePatch()`. It recursively updates a writable target JSONB object, deletes members whose patch value is null, replaces non-object targets for object patches with an empty object shell, and tracks edit deltas so parent payload sizes are repaired.

Aggregates append JSON text incrementally in a `JsonString` stored in aggregate context. The JSONB aggregate variants convert the final accumulated text to JSONB. Window inverse support removes the first serialized aggregate element by scanning over strings and nested containers to find the top-level comma.

The virtual table flow begins with `jsonEachBestIndex()` requiring a usable equality constraint on the hidden `json` column and optionally one on `root`. `jsonEachFilter()` parses JSON/JSONB, resolves the root path, initializes cursor bounds, and chooses either one-level (`json_each`) or recursive (`json_tree`) traversal. `jsonEachNext()` advances by payload-size skipping and maintains a parent stack for recursive paths. `jsonEachColumn()` materializes `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, `path`, and hidden columns.

## State and Persistence Behavior

This file does not persist JSON state to database pages by itself; it computes SQL function results and virtual table rows. JSONB BLOBs returned by `jsonb_*` functions can be stored by callers and later re-enter these routines.

Per-statement parse state may be cached in SQLite auxdata as `JsonCache`, with reference-counted `JsonParse` and `zJson` buffers. Cached parse objects are read-only and are freed when auxdata is destroyed. Editable calls copy cached JSONB before mutation.

Memory allocation follows SQLite DB/context allocators (`sqlite3DbMalloc*`, `sqlite3DbFree`, `sqlite3RCStr*`) and reports OOM through SQLite result APIs. `JsonString` and `JsonParse` carry explicit OOM/error flags to avoid using partially built outputs. Mutation state in `JsonParse.delta` is transient but critical for repairing JSONB parent sizes after edits.

## Dependencies and Integration Points

`json.c` includes `sqliteInt.h` and depends on SQLite internals for memory management, value/result APIs, function registration macros (`JFUNCTION`, `WAGGREGATE`), subtype propagation, UTF-8 helpers, path globbing, printf/str accumulators, virtual table APIs, and test controls.

`sqlite3RegisterJsonFunctions()` is called from `src/func.c` during built-in function registration. `sqlite3JsonVtabRegister()` is declared in `sqliteInt.h` and reached from module creation paths in `src/build.c` for the JSON table-valued functions. Build files include `json.o`, and the manifest/test tree includes focused JSON tests such as `test/json101.test` through `test/json109.test`, `test/json501.test`, `test/json502.test`, and `test/jsonb01.test`.

Compile-time gates shape behavior: `SQLITE_OMIT_JSON` removes the subsystem, `SQLITE_OMIT_VIRTUALTABLE` removes `json_each`/`json_tree`, `SQLITE_OMIT_WINDOWFUNC` removes inverse aggregate behavior, `SQLITE_DEBUG` enables `json_parse` and self-check/debug printing, `SQLITE_JSON_MAX_DEPTH` customizes nesting depth, `SQLITE_LEGACY_JSON_VALID` restores old NULL handling for `json_valid`, and `SQLITE_BUG_COMPATIBLE_20250510` restores an older JSON5 `\0` escape bug.

## Risks and Edge Cases

The largest risk area is malformed or ambiguous JSONB. Some paths intentionally perform superficial validation for performance, so downstream routines must guard each `jsonbPayloadSize()` and type-specific traversal. The code acknowledges that malformed JSONB can sometimes produce an error and sometimes incorrect JSON, so consumers should use strict `json_valid(...,8)` when they require full validation.

Depth handling is security-sensitive because parsing and rendering recurse; the code enforces `JSON_MAX_DEPTH` but edits and virtual table traversal also need correct depth accounting. Payload-size backpatching and `delta` propagation are another high-risk area because a missed parent size adjustment corrupts the JSONB structure after edits.

Compatibility behavior is deliberate but surprising: non-JSONB BLOB inputs may be interpreted as text JSON for historical compatibility, JSON5 extensions are accepted but canonicalized, `json_valid()` defaults to strict canonical text unless flags are supplied, and `->`/`->>` accept abbreviated PostgreSQL-style paths. Small JSONB validation has special rules to avoid false positives for text JSON cast to BLOB.

Aggregate inverse logic edits serialized JSON text by scanning for top-level separators; string escaping and nested bracket tracking are therefore important regression points. Object aggregate NULL-name handling uses `@` sentinels that are removed later, which is subtle and should be tested with window frames and NULL labels.

Virtual table risks include planner contracts around hidden-column constraints, root-path path length/key derivation, malformed input after partial cursor initialization, and parent stack growth. Since `id` values are byte offsets into JSONB rather than stable logical IDs, tests should avoid assuming portability beyond documented behavior.

## Test Signals

Strong test signals are the JSON TCL tests in `sources/storage-engines/sqlite/test/json101.test` through `json109.test`, JSON5 coverage in `json501.test`/`json502.test`, JSONB coverage in `jsonb01.test`, join tests that exercise `json_each`, and `test/json/json-speed-check.sh` for performance-sensitive parser/JSONB behavior. `test/json104.test` specifically maps to `json_patch` and edit/extract semantics.

Useful focused tests for changes in this file include: malformed JSONB validation flags, BLOB-as-text compatibility, JSON5 whitespace/comments/numeric forms, Unicode escapes and surrogate pairs, object label comparison with escaped labels, deep nesting at `JSON_MAX_DEPTH`, all edit operations with size-changing replacements, multiple path extraction, JSONB/text subtype propagation through nested function calls, aggregate window inverse with nested arrays/objects, and `json_each`/`json_tree` with root constraints and malformed roots.
