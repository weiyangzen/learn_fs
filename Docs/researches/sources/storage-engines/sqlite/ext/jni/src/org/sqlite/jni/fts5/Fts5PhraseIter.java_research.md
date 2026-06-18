# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5PhraseIter.java

## Purpose
`Fts5PhraseIter` wraps the native FTS5 phrase-iterator struct used by phrase iteration APIs.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5PhraseIter>` and contains private long fields `a` and `b`, which native code updates and reads.

## Control Flow
Java creates a new iterator, passes it to `Fts5ExtensionApi.xPhraseFirst()` or `xPhraseFirstColumn()`, then repeatedly passes the same object to `xPhraseNext()` or `xPhraseNextColumn()`.

## State and Persistence Behavior
Iterator state is mutable and native-owned. The fields are intentionally opaque to Java code.

## Dependencies and Integration Points
It integrates with `Fts5ExtensionApi` phrase iteration methods and output pointers for column/offset results.

## Risks
Reusing an iterator across different phrase scans or outside the active FTS5 callback can mix stale native state. Java code cannot inspect or repair the internal fields.

## Test Signals
`TesterFts5` uses fresh iterators in `fts5_pinst` and `fts5_pcolinst` auxiliary functions and compares phrase/column/offset lists against expected query results.
