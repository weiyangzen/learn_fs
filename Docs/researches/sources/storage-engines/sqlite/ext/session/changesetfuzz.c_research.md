# sources/storage-engines/sqlite/ext/session/changesetfuzz.c

## Purpose
`changesetfuzz.c` implements a standalone fuzzer for SQLite session changeset and patchset blobs. It either dumps a human-readable representation of an input changeset or produces deterministic mutated changesets that remain structurally well-formed.

The fuzzer deliberately mutates values, changes, groups, and table schemas while preserving core format invariants such as non-NULL primary keys, valid record encodings, and at least one change per table group.

## Important APIs, Types, And Functions
Fuzz operation constants range from value substitution/modification/randomization through change duplication/deletion/type changes, update field removal, indirect flag toggles, group duplication/deletion/swap, and column add/add-PK/delete mutations.

`FuzzChangeset` stores parsed global state: patchset flag, group array, all value pointers, group/change counts, and update count. `FuzzChangesetGroup` stores one table header and its raw change buffer. `FuzzChange` describes one selected mutation and carries replacement value buffers and iteration state.

File and memory helpers include `fuzzReadFile()`, `fuzzWriteFile()`, `fuzzMalloc()`, and `fuzzFree()`. Deterministic pseudo-random generation is provided by a copied RC4-like SQLite PRNG block: `fuzzRandomByte()`, `fuzzRandomBlob()`, `fuzzRandomInt()`, `fuzzRandomU64()`, and `fuzzRandomSeed()`.

Format helpers include `fuzzGetVarint()`, `fuzzPutVarint()`, `fuzzGetI64()`, `fuzzPutU64()`, `fuzzParseHeader()`, `fuzzChangeSize()`, `fuzzParseRecord()`, `fuzzParseChanges()`, and `fuzzParseChangeset()`. Output/dump helpers are `fuzzPrintRecord()` and `fuzzPrintGroup()`. Mutation is selected by `fuzzSelectChange()`, copied/applied by `fuzzCopyChange()`, and emitted by `fuzzDoOneFuzz()`.

## Control Flow
The program accepts either `changesetfuzz INPUT` or `changesetfuzz INPUT SEED N`. It reads and parses the input into borrowed pointers into the original buffer. With one argument, it prints each table group and change. With seed and count, it allocates an output buffer sized to roughly twice the input plus slack, seeds the PRNG, and writes `N` fuzzed files named `INPUT-0`, `INPUT-1`, and so on.

Parsing loops over table headers beginning with `T` for changesets or `P` for patchsets. Each header supplies column count, primary-key array, and table name. Changes are parsed until the next group header. UPDATE changes have old and new records in changesets; patchset DELETE records may include only primary-key fields.

Fuzz selection randomly chooses an operation and target. Invalid choices return negative status, causing the caller to select again. Examples include trying to delete the only group, deleting the only primary-key column, or reducing an UPDATE that only has one updated non-PK column.

Emission recreates group headers and changes while applying the selected mutation. Column additions append NULL or non-NULL PK values as appropriate. Column deletion rewrites PK indexes when needed and drops UPDATE changes that would no longer update any non-PK field. Change type conversions add or remove old/new records according to session format rules.

## State And Persistence Behavior
Parsed state mostly points into the original input changeset; the program does not deep-copy group names, PK arrays, changes, or values. Generated fuzz outputs are written to new files derived from the input filename and overwrite existing files with the same names.

The PRNG is deterministic and single-threaded. Runs with the same input, seed, and count should produce the same output sequence. No database is opened and no changeset is applied in this file.

## Dependencies
The file depends on `sqlite3.h` for op constants, integer typedefs, and memory allocation, plus standard C file/string/assert/ctype headers. It implements changeset binary parsing itself rather than using `sqlite3changeset_start()`, because it needs pointer-level mutation and rewriting.

## Integration Points
This is a fuzzing support utility for the sessions extension. Outputs are intended to feed changeset parsers and appliers while remaining well-formed enough to exercise semantic and conflict paths instead of being rejected immediately as corrupt.

## Risks And Edge Cases
Manual binary parsing is the key risk. `fuzzGetVarint()` assumes available bytes, and several routines rely on earlier bounds checks. Large varints, huge text/blob lengths, malformed table names, and truncated records must consistently return `SQLITE_CORRUPT` without overread.

Output buffer sizing is heuristic (`input*2 + 1024`). Most mutations are bounded, but repeated or unexpectedly large schema/value changes could exceed assumptions if future mutation modes are added. `fuzzPutVarint()` asserts the encoded value is positive and below `2^21`, so extremely wide schemas are not supported.

Value mutation must preserve session invariants. The code avoids setting primary keys to NULL, avoids replacing undefined values incorrectly, and rejects mutations that make updates empty. These constraints are subtle, especially for patchset DELETE records and type conversions between INSERT, DELETE, and UPDATE.

## Test Signals
Good tests should parse and dump changesets and patchsets with integers, reals, NULL, undefined, text, and blobs; verify deterministic output for fixed seeds; and feed generated outputs to SQLite's changeset parser/applier. Mutation-specific tests should cover each `FUZZ_*` mode, PK column deletion rejection, group deletion rejection for single-group inputs, UPDATE field reduction, patchset DELETE handling, and schema column add/delete transformations.
