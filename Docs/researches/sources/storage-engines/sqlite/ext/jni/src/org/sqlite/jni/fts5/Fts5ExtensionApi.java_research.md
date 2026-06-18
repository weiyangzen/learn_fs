# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5ExtensionApi.java

## Purpose
`Fts5ExtensionApi` is the Java wrapper for the FTS5 extension API table offered to auxiliary functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5ExtensionApi>`, exposes singleton `getInstance()`, and native methods for `xColumnCount`, `xColumnSize`, `xColumnText`, `xColumnTotalSize`, auxdata get/set, `xInst`, `xInstCount`, phrase counts/iteration, phrase size, `xQueryPhrase`, `xRowCount`, `xRowid`, `xTokenize`, and `xUserData`. `XQueryPhraseCallback` models the query-phrase callback.

## Control Flow
FTS5 auxiliary functions receive this object, use the current `Fts5Context`, and call native methods to inspect the matched row/query or maintain per-function auxdata.

## State and Persistence Behavior
`getInstance()` returns a singleton API wrapper. Auxdata state is maintained by SQLite/FTS5 and can hold Java objects; if auxdata has an `xDestroy()` method, JNI calls it when FTS5 finalizes that state.

## Dependencies and Integration Points
It depends on `OutputPointer`, `Fts5Context`, `Fts5PhraseIter`, `XTokenizeCallback`, nullable/not-null annotations, and FTS5 function registration through `fts5_api`.

## Risks
Most methods require a valid current `Fts5Context`; misuse outside callbacks can access invalid native state. Column indexes return range errors. Auxdata lifecycle differs from C by omitting an explicit delete callback argument.

## Test Signals
`TesterFts5` validates singleton behavior, user data, column counts/text/sizes/totals, auxdata persistence/clear, instance enumeration, phrase iteration by offset and column, row count, phrase size, query-phrase callbacks, rowid extremes, and tokenization.
