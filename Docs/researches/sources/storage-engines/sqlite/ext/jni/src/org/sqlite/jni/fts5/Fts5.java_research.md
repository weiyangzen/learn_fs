# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5.java

## Purpose
`Fts5` is a final constants holder for FTS5 tokenization flags used by the JNI FTS5 bindings.

## Important APIs, Types, and Functions
It defines `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, `FTS5_TOKENIZE_AUX`, and `FTS5_TOKEN_COLOCATED`. The constructor is private.

## Control Flow
There is no runtime flow. Client or native-facing tokenizer code reads constants.

## State and Persistence Behavior
No mutable state exists.

## Dependencies and Integration Points
The constants correspond to SQLite FTS5 C API tokenization flags and are used with `fts5_tokenizer.xTokenize()` and `XTokenizeCallback`.

## Risks
The file explicitly marks itself incomplete and untested. Drift from SQLite's native constants would break tokenizer behavior.

## Test Signals
There is no direct test in `TesterFts5` for these constants; tokenizer callback tests indirectly cover tokenization through `Fts5ExtensionApi.xTokenize()` rather than custom tokenizer registration.
